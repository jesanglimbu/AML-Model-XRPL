"""Alert tracker: a review queue for analysts working through the model's alerts.

It groups the highest-scored payments into alerts (payments that share an account
within a few hours), ranks them, explains each in plain English, and records what
the analyst decided. Decisions go to an append-only log, so nothing is ever lost:
re-scoring with a new predictions.csv keeps every decision, and a closed alert
comes back into the queue if new suspicious payments join it.

Usage:
    python alert_tracker.py refresh --data ../decode-and-detect-test-data --predictions predictions.csv
    python alert_tracker.py queue                      # what to look at next
    python alert_tracker.py show AL-1a2b3c4d           # the full story of one alert
    python alert_tracker.py escalate AL-1a2b3c4d --by Owen --note "relay, 4 hops in 9 min"
    python alert_tracker.py close AL-1a2b3c4d --by Owen --note "payroll look-alike"
    python alert_tracker.py history AL-1a2b3c4d        # every decision on an alert
    python alert_tracker.py handover --out handover.md # end-of-day summary for the next shift

Only `refresh` reads the payment data. Everything else reads two files in --store:
alerts.json (rebuilt by each refresh) and decisions.csv (never rewritten, only appended to).
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HOUR = 3600
DEFAULT_STORE = "alert_tracker_data"
TOP_SHARE = 0.01         # flag the top 1% of payments (about 400 in the test week)
LINK_WINDOW = 6 * HOUR   # flagged payments sharing an account this close in time form one alert
ACTIONS = {"review": "reviewing", "escalate": "escalated", "close": "closed", "reopen": "open"}
DECISION_COLUMNS = ["logged_at", "alert_id", "action", "status", "analyst", "note", "tx_hashes"]


# ---------- small helpers ----------

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def when(timestamp):
    return datetime.fromtimestamp(int(timestamp), timezone.utc).strftime("%a %d %b %H:%M")


def short(address):
    return f"{address[:8]}…"


def duration(seconds):
    minutes = seconds / 60
    if minutes < 90:
        return f"{minutes:.0f} min"
    if minutes < 48 * 60:
        return f"{minutes / 60:.1f} h"
    return f"{minutes / 1440:.1f} days"


def fail(message):
    sys.exit(f"Error: {message}")


# ---------- storage ----------

def paths(store):
    store = Path(store)
    return store / "alerts.json", store / "decisions.csv"


def load_alerts(store):
    alerts_path, _ = paths(store)
    if not alerts_path.exists():
        fail(f"no alerts in {store}/ yet. Run `python alert_tracker.py refresh --data ... --predictions ...` first.")
    with alerts_path.open() as stream:
        return json.load(stream)


def save_alerts(store, snapshot):
    alerts_path, _ = paths(store)
    alerts_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = alerts_path.with_suffix(".tmp")
    with tmp.open("w") as stream:
        json.dump(snapshot, stream, indent=1)
    os.replace(tmp, alerts_path)   # atomic: a crash never leaves a half-written file


def load_decisions(store):
    _, decisions_path = paths(store)
    if not decisions_path.exists():
        return []
    with decisions_path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def append_decision(store, row):
    _, decisions_path = paths(store)
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not decisions_path.exists()
    with decisions_path.open("a", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=DECISION_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
        stream.flush()
        os.fsync(stream.fileno())


# ---------- building alerts ----------

def read_predictions(path, payments):
    scores = pd.read_csv(path)
    missing = {"TRANSACTION_HASH", "score"} - set(scores.columns)
    if missing:
        fail(f"{path} needs the columns TRANSACTION_HASH,score (missing {sorted(missing)}).")
    if scores.TRANSACTION_HASH.duplicated().any():
        fail(f"{path} lists some transactions more than once.")
    if scores.score.isna().any() or not scores.score.between(0, 1).all():
        fail(f"{path} has scores that are blank or outside 0..1.")
    unknown = ~scores.TRANSACTION_HASH.isin(payments.TRANSACTION_HASH)
    if unknown.all():
        fail(f"none of the transactions in {path} are in the data folder. Wrong --data or --predictions?")
    if unknown.any():
        print(f"Warning: {unknown.sum():,} scored transactions are not in the data and were skipped.")
    unscored = len(payments) - (~unknown).sum()
    if unscored:
        print(f"Warning: {unscored:,} payments in the data have no score and cannot raise alerts.")
    return payments.merge(scores[["TRANSACTION_HASH", "score"]], on="TRANSACTION_HASH")


def group_flagged(flagged, window):
    """Union payments that share an account within `window` seconds into one alert."""
    parent = list(range(len(flagged)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_account = defaultdict(list)
    for i, row in enumerate(flagged.itertuples()):
        by_account[row.FROM_ADDRESS].append((row.TIMESTAMP, i))
        by_account[row.TO_ADDRESS].append((row.TIMESTAMP, i))
    for events in by_account.values():
        events.sort()
        for (t1, i), (t2, j) in zip(events, events[1:]):
            if t2 - t1 <= window:
                parent[find(i)] = find(j)
    return [find(i) for i in range(len(flagged))]


def has_cycle(edges):
    graph = defaultdict(set)
    for s, d in edges:
        graph[s].add(d)
    state = {}

    def visit(node):
        state[node] = "active"
        for nxt in graph[node]:
            if state.get(nxt) == "active" or (nxt not in state and visit(nxt)):
                return True
        state[node] = "done"
        return False

    return any(node not in state and visit(node) for node in list(graph))


def explain(group):
    """Plain-English reasons built only from the alert's own payments."""
    reasons = []
    edges = list(zip(group.FROM_ADDRESS, group.TO_ADDRESS))
    payees = group.groupby("FROM_ADDRESS").TO_ADDRESS.nunique()
    payers = group.groupby("TO_ADDRESS").FROM_ADDRESS.nunique()
    if payees.max() >= 3:
        reasons.append(f"fan-out: `{short(payees.idxmax())}` paid {payees.max()} different accounts")
    if payers.max() >= 3:
        reasons.append(f"fan-in: `{short(payers.idxmax())}` was paid by {payers.max()} different accounts")

    # Accounts that received money and then sent money on inside this alert.
    gaps = []
    for account in set(group.TO_ADDRESS) & set(group.FROM_ADDRESS):
        received = group[group.TO_ADDRESS == account].TIMESTAMP
        sent = group[group.FROM_ADDRESS == account].TIMESTAMP
        later = sent[sent >= received.min()]
        if len(later):
            gaps.append(later.min() - received.min())
    if gaps:
        reasons.append(f"relay: {len(gaps)} account(s) passed money on, typically "
                       f"{duration(sorted(gaps)[len(gaps) // 2])} after receiving it")
    if has_cycle(edges):
        reasons.append("cycle: money comes back to an account it already left")
    if len(group) >= 3 and group.VALUE.std() / group.VALUE.mean() < 0.15:
        reasons.append(f"similar amounts: {len(group)} payments all close to ${group.VALUE.mean():,.0f}")
    if not reasons:
        reasons.append("no clear shape; the model's score comes from a mix of weaker signals")
    return reasons


def build_alerts(payments, top_share, window):
    payments = payments.sort_values(["TIMESTAMP", "TRANSACTION_HASH"]).reset_index(drop=True)
    n_flag = max(1, round(len(payments) * top_share))
    cutoff = payments.score.nlargest(n_flag).min()
    flagged = payments[payments.score >= cutoff].reset_index(drop=True)
    flagged["group"] = group_flagged(flagged, window)

    alerts = []
    for _, group in flagged.groupby("group"):
        group = group.sort_values(["TIMESTAMP", "TRANSACTION_HASH"])
        first = group.iloc[0]
        alerts.append({
            "alert_id": f"AL-{first.TRANSACTION_HASH[:8].lower()}",
            "risk": round(float(group.score.max()), 4),
            "mean_score": round(float(group.score.mean()), 4),
            "n_payments": len(group),
            "accounts": sorted(set(group.FROM_ADDRESS) | set(group.TO_ADDRESS)),
            "total_usd": round(float(group.VALUE.sum()), 2),
            "start": int(group.TIMESTAMP.min()),
            "end": int(group.TIMESTAMP.max()),
            "reasons": explain(group),
            "payments": [{"hash": r.TRANSACTION_HASH, "time": int(r.TIMESTAMP), "from": r.FROM_ADDRESS,
                          "to": r.TO_ADDRESS, "usd": round(float(r.VALUE), 2), "score": round(float(r.score), 4)}
                         for r in group.itertuples()],
        })
    alerts.sort(key=lambda a: (-a["risk"], -a["n_payments"], a["alert_id"]))
    for rank, alert in enumerate(alerts, 1):
        alert["rank"] = rank
    return alerts, float(cutoff), len(flagged)


# ---------- status: replaying the decision log ----------

def statuses(alerts, decisions):
    """Each alert's current status, carried over by shared payments if the alert was regrouped.

    A decision covers the payments the analyst saw. If a closed or escalated alert now
    contains payments no decision covered, it is reopened so someone looks at them.
    """
    latest_by_tx = {}
    for d in decisions:                       # the log is in time order, so later wins
        for h in d["tx_hashes"].split(";"):
            latest_by_tx[h] = d
    result = {}
    for alert in alerts:
        hashes = [p["hash"] for p in alert["payments"]]
        decided = [latest_by_tx[h] for h in hashes if h in latest_by_tx]
        if not decided:
            result[alert["alert_id"]] = {"status": "new", "decision": None, "unseen": len(hashes)}
            continue
        last = max(decided, key=lambda d: d["logged_at"])
        unseen = sum(h not in latest_by_tx for h in hashes)
        status = last["status"]
        if unseen and status in ("closed", "escalated"):
            status = "reopened"
        result[alert["alert_id"]] = {"status": status, "decision": last, "unseen": unseen}
    return result


STATUS_ORDER = {"reopened": 0, "new": 1, "open": 1, "reviewing": 2, "escalated": 3, "closed": 4}


# ---------- commands ----------

def cmd_refresh(args):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from case_summary import load        # the organisers' loader, valued in USD

    print(f"Loading payments from {args.data} ...")
    payments = read_predictions(args.predictions, load(args.data))
    alerts, cutoff, n_flagged = build_alerts(payments, args.top_share, args.window_hours * HOUR)
    previous = paths(args.store)[0]
    old_ids = {a["alert_id"] for a in json.load(previous.open())["alerts"]} if previous.exists() else set()
    save_alerts(args.store, {
        "refreshed_at": now(), "data": str(args.data), "predictions": str(args.predictions),
        "score_cutoff": cutoff, "flagged_payments": n_flagged, "total_payments": len(payments),
        "window_hours": args.window_hours, "alerts": alerts,
    })
    state = statuses(alerts, load_decisions(args.store))
    counts = Counter(s["status"] for s in state.values())
    print(f"Flagged {n_flagged:,} of {len(payments):,} payments (score >= {cutoff:.3f}) "
          f"into {len(alerts):,} alerts.")
    if old_ids:
        print(f"{len(set(state) - old_ids):,} alert IDs are new since the last refresh.")
    print("Status: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: STATUS_ORDER[kv[0]])))
    if counts["reopened"]:
        print(f"Note: {counts['reopened']} decided alert(s) reopened because new flagged payments joined them.")
    print("Next: python alert_tracker.py queue")


def queue_rows(snapshot, state, show_all):
    rows = []
    for a in snapshot["alerts"]:
        s = state[a["alert_id"]]
        if not show_all and s["status"] in ("closed", "escalated"):
            continue
        rows.append((STATUS_ORDER[s["status"]] if s["status"] == "reopened" else 1, a["rank"], a, s))
    rows.sort(key=lambda r: (r[0], r[1]))
    return [(a, s) for _, _, a, s in rows]


def cmd_queue(args):
    snapshot = load_alerts(args.store)
    state = statuses(snapshot["alerts"], load_decisions(args.store))
    rows = queue_rows(snapshot, state, args.all)
    total = len(snapshot["alerts"])
    done = sum(s["status"] in ("closed", "escalated") for s in state.values())
    print(f"Scores from {snapshot['predictions']} (refreshed {snapshot['refreshed_at']}). "
          f"{done} of {total} alerts decided.\n")
    if not rows:
        print("Nothing left to review. Run `handover` to write up the day.")
        return
    print(f"{'#':>4}  {'alert':<12} {'status':<10} {'risk':>5}  {'pays':>4}  {'total USD':>12}  {'span':>9}  why")
    for a, s in rows[:args.limit]:
        print(f"{a['rank']:>4}  {a['alert_id']:<12} {s['status']:<10} {a['risk']:>5.2f}  {a['n_payments']:>4}  "
              f"{a['total_usd']:>12,.0f}  {duration(a['end'] - a['start']):>9}  {a['reasons'][0]}")
    if len(rows) > args.limit:
        print(f"\n... and {len(rows) - args.limit} more (use --limit).")
    print("\nNext: python alert_tracker.py show <alert>")


def normalise(alert_id):
    return "AL-" + alert_id.lower().removeprefix("al-")


def find_alert(snapshot, alert_id, store):
    alert_id = normalise(alert_id)
    for a in snapshot["alerts"]:
        if a["alert_id"] == alert_id:
            return a
    # Re-scoring can regroup payments; point the analyst to where an old alert went.
    old = {h for d in load_decisions(store) if d["alert_id"] == alert_id for h in d["tx_hashes"].split(";")}
    if old:
        now_in = [a["alert_id"] for a in snapshot["alerts"] if old & {p["hash"] for p in a["payments"]}]
        where = f"Its payments are now in: {', '.join(now_in)}." if now_in else "None of its payments are flagged any more."
        fail(f"{alert_id} was regrouped by the last refresh. {where} Its decisions are kept in the log.")
    fail(f"no alert {alert_id} in the current queue. Run `queue --all` to see every alert.")


def cmd_show(args):
    snapshot = load_alerts(args.store)
    decisions = load_decisions(args.store)
    alert = find_alert(snapshot, args.alert, args.store)
    s = statuses([alert], decisions)[alert["alert_id"]]
    print(f"{alert['alert_id']}  —  rank {alert['rank']} of {len(snapshot['alerts'])}, "
          f"status {s['status'].upper()}, risk {alert['risk']:.2f}")
    print(f"{alert['n_payments']} flagged payments, ${alert['total_usd']:,.0f}, {len(alert['accounts'])} accounts, "
          f"{when(alert['start'])} to {when(alert['end'])} UTC ({duration(alert['end'] - alert['start'])})\n")
    print("Why it is here:")
    for r in alert["reasons"]:
        print(f"  - {r}")
    print("\nPayments (oldest first):")
    for p in alert["payments"]:
        print(f"  {when(p['time'])}  {short(p['from'])} -> {short(p['to'])}  ${p['usd']:>12,.2f}  "
              f"score {p['score']:.2f}  {p['hash']}")
    if s["decision"]:
        d = s["decision"]
        print(f"\nLast decision: {d['status']} by {d['analyst']} at {d['logged_at']}: {d['note']}")
        if s["unseen"]:
            print(f"  {s['unseen']} payment(s) above joined this alert after that decision. Please re-check.")
    print("\nScores rank payments for review; they are not proof. Check the hashes before escalating.")
    print(f"Decide: python alert_tracker.py escalate|close|review {alert['alert_id']} --by NAME --note \"...\"")


def cmd_decide(args):
    snapshot = load_alerts(args.store)
    alert = find_alert(snapshot, args.alert, args.store)
    note = (args.note or "").strip()
    if args.command in ("close", "escalate") and not note:
        fail(f"`{args.command}` needs --note so the next analyst knows why.")
    status = ACTIONS[args.command]
    append_decision(args.store, {
        "logged_at": now(), "alert_id": alert["alert_id"], "action": args.command, "status": status,
        "analyst": args.by, "note": note, "tx_hashes": ";".join(p["hash"] for p in alert["payments"]),
    })
    print(f"{alert['alert_id']} is now {status.upper()} (by {args.by}). Saved to {paths(args.store)[1]}.")


def cmd_history(args):
    alert_id = normalise(args.alert)
    decisions = load_decisions(args.store)
    current = [a for a in load_alerts(args.store)["alerts"] if a["alert_id"] == alert_id]
    hashes = {p["hash"] for p in current[0]["payments"]} if current else set()
    rows = [d for d in decisions if d["alert_id"] == alert_id or hashes & set(d["tx_hashes"].split(";"))]
    if not rows:
        print(f"No decisions recorded on {alert_id} yet.")
    for d in rows:
        note = f": {d['note']}" if d["note"] else ""
        print(f"{d['logged_at']}  {d['status']:<10} by {d['analyst']} (as {d['alert_id']}){note}")


def cmd_handover(args):
    snapshot = load_alerts(args.store)
    decisions = load_decisions(args.store)
    state = statuses(snapshot["alerts"], decisions)
    by_status = defaultdict(list)
    for a in snapshot["alerts"]:
        by_status[state[a["alert_id"]]["status"]].append(a)
    counts = {k: len(v) for k, v in by_status.items()}

    lines = [f"# Alert handover — {now()}", "",
             f"Scores: `{snapshot['predictions']}` (refreshed {snapshot['refreshed_at']}). "
             f"{snapshot['flagged_payments']:,} of {snapshot['total_payments']:,} payments flagged "
             f"into {len(snapshot['alerts']):,} alerts.", "",
             "| Status | Alerts |", "|---|---|"]
    for status in sorted(counts, key=STATUS_ORDER.get):
        lines.append(f"| {status} | {counts[status]} |")

    def section(title, alerts, with_note):
        lines.extend(["", f"## {title}", ""])
        if not alerts:
            lines.append("None.")
        for a in sorted(alerts, key=lambda a: a["rank"]):
            d = state[a["alert_id"]]["decision"]
            extra = f" — {d['analyst']}: {d['note']}" if with_note and d else ""
            lines.append(f"- **{a['alert_id']}** (rank {a['rank']}, risk {a['risk']:.2f}, {a['n_payments']} payments, "
                         f"${a['total_usd']:,.0f}) {a['reasons'][0]}{extra}")

    section("Escalated", by_status["escalated"], True)
    section("Reopened: new payments joined an alert that was already decided", by_status["reopened"], True)
    section("In review, not finished", by_status["reviewing"], True)
    untouched = by_status["new"] + by_status["open"]
    section(f"Not yet looked at (highest {min(args.top, len(untouched))} of {len(untouched)})",
            sorted(untouched, key=lambda a: a["rank"])[:args.top], False)
    lines.extend(["", f"{len(decisions)} decisions in the log. Synthetic data: no real people or accounts.", ""])

    text = "\n".join(lines)
    if args.out:
        Path(args.out).write_text(text)
        print(f"Handover saved to {args.out}")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--store", default=DEFAULT_STORE, help=f"where alerts and decisions live (default {DEFAULT_STORE}/)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("refresh", help="build the alert queue from a predictions file")
    p.add_argument("--data", required=True, help="folder with transactions.parquet and market_rates.csv")
    p.add_argument("--predictions", required=True, help="CSV with TRANSACTION_HASH,score")
    p.add_argument("--top-share", type=float, default=TOP_SHARE, help="share of payments to flag (default 0.01)")
    p.add_argument("--window-hours", type=float, default=LINK_WINDOW / HOUR,
                   help="link flagged payments sharing an account within this many hours (default 6)")
    p.set_defaults(run=cmd_refresh)

    p = sub.add_parser("queue", help="alerts still to review, riskiest first")
    p.add_argument("--all", action="store_true", help="include closed and escalated alerts")
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(run=cmd_queue)

    p = sub.add_parser("show", help="everything about one alert")
    p.add_argument("alert")
    p.set_defaults(run=cmd_show)

    for action, help_text in [("review", "mark as being looked at"), ("escalate", "send for investigation"),
                              ("close", "no further action"), ("reopen", "put back in the queue")]:
        p = sub.add_parser(action, help=help_text)
        p.add_argument("alert")
        p.add_argument("--by", required=True, help="your name")
        p.add_argument("--note", help="why (required for close and escalate)")
        p.set_defaults(run=cmd_decide)

    p = sub.add_parser("history", help="every decision recorded on an alert")
    p.add_argument("alert")
    p.set_defaults(run=cmd_history)

    p = sub.add_parser("handover", help="end-of-day summary for the next analyst")
    p.add_argument("--out", help="save as Markdown")
    p.add_argument("--top", type=int, default=10, help="how many unreviewed alerts to list")
    p.set_defaults(run=cmd_handover)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
