"""Case summary writer: turns flagged payments into short reports an investigator can read.

Step 1 gathers facts about a payment with pandas (no AI).
Step 2 writes them up using templates, so it runs without an API key.

Usage:
    python case_summary.py --data ../decode-and-detect-test-data --predictions predictions.csv --top 5
    python case_summary.py --data ../decode-and-detect-test-data --tx <TRANSACTION_HASH>
"""
import argparse
from datetime import datetime, timezone

import pandas as pd

from payments import load_payments

HOUR = 3600
DAY = 24 * HOUR

# How strong a signal has to be before it counts as a red flag.
FORWARD_SHARE = 0.8      # receiver passes on at least 80% of the payment...
FORWARD_WINDOW = HOUR    # ...within an hour
BURST_WINDOW = HOUR      # fan-out / fan-in are counted within an hour either side
BURST_ACCOUNTS = 5       # this many different accounts in that window is a burst
LARGE_MULTIPLE = 5       # payment is 5x the sender's usual size
TRAIL_HOPS = 3           # how far to follow the money
TRAIL_BRANCHES = 5       # biggest onward payments to follow at each hop


def load(directory):
    df = pd.DataFrame(load_payments(directory))
    df["TIMESTAMP"] = df.TIMESTAMP.astype(int)
    return df.sort_values("TIMESTAMP").reset_index(drop=True)


def short(address):
    return f"{address[:8]}…"


def when(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%a %d %b %H:%M UTC")


def usd(amount):
    return f"${amount:,.2f}"


# ---------- Step 1: facts ----------

def account_profile(df, account):
    """What an account does over the whole week."""
    sent = df[df.FROM_ADDRESS == account]
    got = df[df.TO_ADDRESS == account]
    usd_sent, usd_got = sent.VALUE.sum(), got.VALUE.sum()
    return {
        "payments_sent": len(sent),
        "payments_received": len(got),
        "usd_sent": usd_sent,
        "usd_received": usd_got,
        "pass_through": usd_sent / usd_got if usd_got else None,
        "different_payees": sent.TO_ADDRESS.nunique(),
        "different_payers": got.FROM_ADDRESS.nunique(),
        "median_payment_sent": sent.VALUE.median() if len(sent) else None,
    }


def follow_money(df, start_account, start_time, start_amount, hops=TRAIL_HOPS):
    """Follow money onward from an account, hop by hop.

    At each hop, take the payments the account sent within an hour of receiving
    the money. Team 1's money trail tracker can replace this function.
    """
    trail, frontier, seen = [], [(start_account, start_time, start_amount)], {start_account}
    for hop in range(1, hops + 1):
        next_frontier = []
        for account, t, _ in frontier:
            onward = df[(df.FROM_ADDRESS == account) & (df.TIMESTAMP > t)
                        & (df.TIMESTAMP <= t + FORWARD_WINDOW)]
            for row in onward.nlargest(TRAIL_BRANCHES, "VALUE").itertuples():
                trail.append({"hop": hop, "from": account, "to": row.TO_ADDRESS,
                              "usd": row.VALUE, "minutes_later": (row.TIMESTAMP - t) / 60,
                              "time": row.TIMESTAMP})
                if row.TO_ADDRESS not in seen:
                    seen.add(row.TO_ADDRESS)
                    next_frontier.append((row.TO_ADDRESS, row.TIMESTAMP, row.VALUE))
        frontier = next_frontier
        if not frontier:
            break
    return trail


def gather_facts(df, tx_hash, score=None):
    tx = df[df.TRANSACTION_HASH == tx_hash].iloc[0]
    t, value = tx.TIMESTAMP, tx.VALUE
    sender, receiver = tx.FROM_ADDRESS, tx.TO_ADDRESS

    # Did the receiver pass the money straight on?
    onward = df[(df.FROM_ADDRESS == receiver) & (df.TIMESTAMP > t) & (df.TIMESTAMP <= t + FORWARD_WINDOW)]
    # Had the sender only just received it?
    incoming = df[(df.TO_ADDRESS == sender) & (df.TIMESTAMP >= t - FORWARD_WINDOW) & (df.TIMESTAMP < t)]
    # Fan-out from the sender and fan-in to the receiver around this time.
    near = df[(df.TIMESTAMP >= t - BURST_WINDOW) & (df.TIMESTAMP <= t + BURST_WINDOW)]

    trail = follow_money(df, receiver, t, value)

    sender_profile = account_profile(df, sender)
    usual = sender_profile["median_payment_sent"]
    return {
        "tx_hash": tx_hash,
        "score": score,
        "time": t,
        "sender": sender,
        "receiver": receiver,
        "usd": value,
        "sender_profile": sender_profile,
        "receiver_profile": account_profile(df, receiver),
        "forwarded_usd_1h": onward.VALUE.sum(),
        "forwarded_count_1h": len(onward),
        "minutes_to_forward": (onward.TIMESTAMP.min() - t) / 60 if len(onward) else None,
        "sender_received_usd_1h_before": incoming.VALUE.sum(),
        "sender_payees_nearby": near[near.FROM_ADDRESS == sender].TO_ADDRESS.nunique(),
        "receiver_payers_nearby": near[near.TO_ADDRESS == receiver].FROM_ADDRESS.nunique(),
        "times_usual_size": value / usual if usual else None,
        "trail": trail,
        "money_returns_to_sender": any(step["to"] == sender for step in trail),
    }


def red_flags(f):
    """Each red flag is (short reason, sentence for the report)."""
    flags = []
    if f["forwarded_usd_1h"] >= FORWARD_SHARE * f["usd"]:
        share = f["forwarded_usd_1h"] / f["usd"]
        amount = f"{share:.0%} of this payment" if share <= 1.1 else "more than this payment"
        flags.append(("relay", f"Within an hour the receiver sent out {usd(f['forwarded_usd_1h'])} "
                      f"({amount}), the first onward payment after {f['minutes_to_forward']:.0f} minutes."))
    if f["sender_received_usd_1h_before"] >= FORWARD_SHARE * f["usd"]:
        flags.append(("pass-on", f"The sender had received {usd(f['sender_received_usd_1h_before'])} "
                      "in the hour before, so it may be passing on money it was just given."))
    if f["sender_payees_nearby"] >= BURST_ACCOUNTS:
        flags.append(("fan-out", f"The sender paid {f['sender_payees_nearby']} different accounts "
                      "within an hour of this payment."))
    if f["receiver_payers_nearby"] >= BURST_ACCOUNTS:
        flags.append(("fan-in", f"The receiver was paid by {f['receiver_payers_nearby']} different "
                      "accounts within an hour of this payment."))
    if f["money_returns_to_sender"]:
        flags.append(("cycle", "Following the money onward, some of it comes back to the original sender."))
    for role in ("sender", "receiver"):
        p = f[f"{role}_profile"]
        if p["pass_through"] and 0.8 <= p["pass_through"] <= 1.25 and p["payments_received"] >= 5:
            flags.append((f"{role} pass-through", f"Over the week, the {role} sent on "
                          f"{p['pass_through']:.0%} of everything it received, keeping almost none."))
    if f["times_usual_size"] and f["times_usual_size"] >= LARGE_MULTIPLE:
        flags.append(("unusually large", f"This payment is {f['times_usual_size']:.0f}x the sender's "
                      "usual payment size."))
    return flags


# ---------- Step 2: words ----------

def describe_profile(name, p):
    return (f"- **{name}** sent {p['payments_sent']} payments ({usd(p['usd_sent'])}) to "
            f"{p['different_payees']} accounts and received {p['payments_received']} "
            f"({usd(p['usd_received'])}) from {p['different_payers']} accounts this week.")


def write_report(f):
    flags = red_flags(f)
    score = f" — score {f['score']:.2f}" if f["score"] is not None else ""
    lines = [
        f"## Case {f['tx_hash'][:12]}{score}",
        "",
        f"{when(f['time'])}: account `{short(f['sender'])}` paid {usd(f['usd'])} "
        f"to `{short(f['receiver'])}`.",
        "",
    ]

    if flags:
        lines.append("**Red flags**")
        lines += [f"- {sentence}" for _, sentence in flags]
    else:
        lines.append("No single red flag stands out; the score comes from a combination of weaker signals.")
    lines.append("")

    lines.append("**Accounts involved**")
    lines.append(describe_profile(f"Sender `{short(f['sender'])}`", f["sender_profile"]))
    lines.append(describe_profile(f"Receiver `{short(f['receiver'])}`", f["receiver_profile"]))
    lines.append("")

    if f["trail"]:
        lines.append("**Where the money went next** (onward payments within an hour of each hop)")
        for step in f["trail"]:
            lines.append(f"- Hop {step['hop']}: `{short(step['from'])}` → `{short(step['to'])}` "
                         f"{usd(step['usd'])}, {step['minutes_later']:.0f} min later")
    else:
        lines.append("The receiver did not send any money on within an hour.")
    lines.append("")
    return "\n".join(lines)


def reason(f):
    """One short line for the optional `reason` column in the predictions CSV."""
    return "; ".join(name for name, _ in red_flags(f)) or "combination of weaker signals"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", required=True, help="folder with transactions.parquet and market_rates.csv")
    parser.add_argument("--predictions", help="CSV with TRANSACTION_HASH,score (from the alert ranker)")
    parser.add_argument("--top", type=int, default=5, help="how many of the highest scores to summarise")
    parser.add_argument("--tx", nargs="*", default=[], help="summarise these transaction hashes instead")
    parser.add_argument("--out", help="save the reports to this Markdown file")
    parser.add_argument("--reasons-csv", help="save the predictions with a `reason` column for the top cases")
    args = parser.parse_args()

    df = load(args.data)
    scores = pd.read_csv(args.predictions) if args.predictions else None

    if args.tx:
        cases = args.tx
    elif scores is not None:
        cases = scores.nlargest(args.top, "score").TRANSACTION_HASH.tolist()
    else:
        parser.error("give --predictions or --tx")

    score_of = dict(zip(scores.TRANSACTION_HASH, scores.score)) if scores is not None else {}
    facts = [gather_facts(df, h, score_of.get(h)) for h in cases]
    reports = "\n".join(write_report(f) for f in facts)

    if args.out:
        with open(args.out, "w") as stream:
            stream.write(f"# Case summaries\n\n{reports}")
        print(f"Saved {len(facts)} reports to {args.out}")
    else:
        print(reports)

    if args.reasons_csv:
        if scores is None:
            parser.error("--reasons-csv needs --predictions")
        reasons = {f["tx_hash"]: reason(f) for f in facts}
        scores["reason"] = scores.TRANSACTION_HASH.map(reasons).fillna("")
        scores.to_csv(args.reasons_csv, index=False)
        print(f"Saved predictions with reasons to {args.reasons_csv}")


if __name__ == "__main__":
    main()
