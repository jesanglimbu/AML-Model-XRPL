"""CASE SUMMARY WRITER.  Owner: person D

Input : outputs/ranked_alerts.json
Output: outputs/summaries.json + outputs/summaries.md

Rule: EVERY claim cites a real transaction hash from the alert.
  1. Facts built in code (amounts, times, hashes, roles, pattern) -> can't be wrong.
  2. Template -> English (works with no API key, no LLM at runtime).
  3. OPTIONAL (TODO): polish_with_llm() rewrites wording; verify_citations()
     rejects any output that mentions a hash not in the alert.
"""
import json
import os
import re
import statistics
from datetime import datetime, timezone

import networkx as nx

import config


REPORT_INTRO = """These reports explain why groups of payments were flagged as possible money laundering.
They are based on a week of **synthetic** payments on a fictional XRPL-style ledger, valued in
US dollars. Nothing here is a real person, account or allegation.

> **A flag is a reason to investigate, not evidence of wrongdoing.** Roughly 1 in 12 of the payments
> our model ranks most suspicious is a false alarm, so every case needs a human review.

Each case is one **alert**: a group of linked payments our model flagged together. The **risk score**
(0 to 1) ranks the alerts, riskiest first. Each report names the pattern, shows who sent, passed on
and collected the money, explains why it was flagged, and lists every payment with its hash.

"""

GLOSSARY = """## How to read these reports

| Term | Meaning |
|---|---|
| Risk score | How suspicious the whole alert looks, from 0 (normal) to 1 (very suspicious). Used to decide which cases to look at first |
| Model probability | How suspicious one single payment looks to our model, from 0 to 1 |
| Linked payments / burst | Payments connected to each other (the same money moving on, splitting or joining) within 10 minutes |
| Pattern | The shape of the money flow: fan-out (one account splits money), fan-in (many pay one), chain (passed along a line), split and recombine, layering (through intermediaries), or cycle (money comes back) |
| Source / intermediary / collector | Accounts that only send, that receive and send on, and that only receive, within the alert |
| Passed on after N min | How long an intermediary held money before sending it on. Minutes, or less, is typical of mules |
| Passed funds on within N min | The receiver sent money onward almost immediately, the typical sign of a money mule or relay account |
| Forwarded funds N min after receiving them | The sender was passing on money it had only just been given, rather than spending its own |
| Forwarded N% of the amount it last received | The account kept almost nothing and passed nearly everything on (a pass-through account) |
| Sender involved in N other payments within 5 min | Many payments in a very short time, often money being split up (fan-out) or collected (fan-in) |
| `tx …` | The start of a transaction hash, so every claim can be checked against the data |

**Why speed matters:** legitimate payments can have the same shapes as laundering (chains,
splits, cycles). What gives laundering away is how **fast** the money moves from account to account.

"""


def short(addr):
    return addr[:6] + "…" + addr[-4:]


def cite(h):
    if config.EXPLORER_TX:
        return f"[tx {h[:8]}]({config.EXPLORER_TX}{h})"
    return f"`tx {h[:12]}`"


def seconds(iso):
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def roles(a):
    """Sources only send, collectors only receive, intermediaries do both (within the alert)."""
    senders = {s for s, _ in a["edges"]}
    receivers = {d for _, d in a["edges"]}
    middle = senders & receivers
    return sorted(senders - middle), sorted(middle), sorted(receivers - middle)


def pattern(a):
    """Name the shape of the money flow, with a one-line explanation."""
    g = nx.DiGraph(a["edges"])
    if not nx.is_directed_acyclic_graph(g):
        return "Cycle", "money goes round and comes back to an account it already passed through"
    sources, middle, collectors = roles(a)
    if not middle:
        if len(sources) == 1 and len(collectors) == 1:
            return "Repeated payments", "one account pays the same account several times in quick succession"
        if len(sources) == 1:
            return "Fan-out", "one account splits money across many accounts"
        if len(collectors) == 1:
            return "Fan-in", "many accounts send money into one account"
        return "Many-to-many", "several accounts pay several other accounts in one short burst"
    if all(g.in_degree(n) <= 1 and g.out_degree(n) <= 1 for n in g):
        return "Chain", "money is passed along a line of accounts, one after another"
    if len(sources) == 1 and len(collectors) == 1:
        return "Split and recombine", "money is split across intermediaries and collected again in one account"
    return "Layering", "money is moved through intermediary accounts, hiding where it came from and where it ends up"


def pass_on_minutes(a):
    """For each onward payment by an intermediary: minutes since it last received money in this alert."""
    last_received, gaps = {}, []
    for (s, d), t in zip(a["edges"], map(seconds, a["times"])):
        if s in last_received:
            gaps.append((t - last_received[s]) / 60)
        last_received[d] = t
    return gaps


def accounts_text(accounts, one, many):
    if not accounts:
        return f"no {many}"
    names = ", ".join(f"`{short(x)}`" for x in accounts[:3]) + (" …" if len(accounts) > 3 else "")
    return f"**{len(accounts)} {one if len(accounts) == 1 else many}** ({names})"


def why_flagged(a):
    """Alert-level reasons, plus the ranker's per-payment reasons without repeats.

    Burst-size reasons are dropped: they describe 3-minute bursts and would contradict the
    alert's own size and duration, which are stated here instead.
    """
    n, probs = len(a["tx_hashes"]), a["probabilities"]
    reasons = [f"{n} linked payments between {len(a['accounts'])} accounts in {a['minutes_total']} minutes"]
    gaps = pass_on_minutes(a)
    if gaps:
        reasons.append(f"intermediaries passed money on a median of {statistics.median(gaps):.1f} min "
                       f"after receiving it (fastest {min(gaps):.1f} min)")
    reasons.append(f"every payment scored at least {min(probs):.2f} by the model (average {sum(probs) / n:.2f})")
    seen = set()
    for r in a["reasons"]:
        if r.startswith("part of a burst") or "flagged payments, total" in r or r in seen:
            continue
        seen.add(r)
        reasons.append(r)
    return reasons


def graph_link(a):
    path = f"{config.GRAPH_DIR}/{a['alert_id']}.png"
    if not os.path.exists(path):
        return None
    return f"![Money trail for {a['alert_id']}]({os.path.relpath(path, os.path.dirname(config.SUMMARIES_MD))})"


def template_summary(a):
    n = len(a["tx_hashes"])
    total = sum(a["amounts_usd"])
    name, meaning = pattern(a)
    sources, middle, collectors = roles(a)
    lines = [
        f"### {a['alert_id']} — risk {a['risk_score']:.2f}",
        "",
        f"**Pattern: {name}** — {meaning}.",
        "",
        f"Between {a['times'][0][11:16]} and {a['times'][-1][11:16]} UTC on {a['times'][0][:10]}, "
        f"**{n} linked payments** worth **${total:,.0f}** moved between **{len(a['accounts'])} accounts** "
        f"in **{a['minutes_total']} minutes**. It started when `{short(a['edges'][0][0])}` paid "
        f"`{short(a['edges'][0][1])}` {cite(a['tx_hashes'][0])} and ended with a payment to "
        f"`{short(a['edges'][-1][1])}` {cite(a['tx_hashes'][-1])}.",
        "",
        f"**Who's who:** {accounts_text(sources, 'source', 'sources')} → "
        f"{accounts_text(middle, 'intermediary', 'intermediaries')} → "
        f"{accounts_text(collectors, 'collector', 'collectors')}.",
        "",
        "**Why it was flagged:**",
    ]
    lines += [f"- {r}" for r in why_flagged(a)]
    graph = graph_link(a)
    if graph:
        lines += ["", graph]
    lines += ["", "**Payments:**"]
    for i, h in enumerate(a["tx_hashes"]):
        s, d = a["edges"][i]
        lines.append(f"{i + 1}. {a['times'][i][11:19]} `{short(s)}` → `{short(d)}`: "
                     f"{a['amounts'][i]:,.2f} {a['assets'][i]} (${a['amounts_usd'][i]:,.0f}), "
                     f"model probability {a['probabilities'][i]:.2f} {cite(h)}")
    return "\n".join(lines)


def polish_with_llm(text, alert):
    """TODO (optional): rewrite `text` with an LLM for a compliance analyst,
    WITHOUT adding facts. Until implemented, returns the template unchanged."""
    return text


def verify_citations(text, alert):
    real = alert["tx_hashes"]
    cited_prefixes = set(re.findall(r"tx ([0-9A-F]{8,64})", text))
    cited = sorted({h for h in real for c in cited_prefixes if h.startswith(c)})
    ok = all(any(h.startswith(c) for h in real) for c in cited_prefixes)
    return ok, cited


def write(ranked):
    out = []
    for a in ranked[:config.TOP_N_SUMMARIES]:
        base = template_summary(a)
        text = polish_with_llm(base, a)
        ok, cited = verify_citations(text, a)
        if not ok:
            text = base
            ok, cited = verify_citations(text, a)
        out.append({"alert_id": a["alert_id"], "risk_score": a["risk_score"],
                    "summary": text, "cited_hashes": cited})
    return out


def save(summaries):
    json.dump(summaries, open(config.SUMMARIES_JSON, "w"), indent=2)
    with open(config.SUMMARIES_MD, "w", encoding="utf-8") as f:
        f.write("# Case summaries\n\n" + REPORT_INTRO + GLOSSARY + "---\n\n"
                + "\n\n---\n\n".join(s["summary"] for s in summaries))


if __name__ == "__main__":
    save(write(json.load(open(config.RANKED_JSON))))
    print(f"summaries -> {config.SUMMARIES_MD}")
