"""CASE SUMMARY WRITER.  Owner: person D

Input : outputs/ranked_alerts.json
Output: outputs/summaries.json + outputs/summaries.md

Rule: EVERY claim cites a real transaction hash from the alert.
  1. Facts built in code (amounts, times, hashes) -> can't be wrong.
  2. Template -> English (works with no API key).
  3. OPTIONAL (TODO): polish_with_llm() rewrites wording; verify_citations()
     rejects any output that mentions a hash not in the alert.
"""
import json
import re

import config


REPORT_INTRO = """These reports explain why groups of payments were flagged as possible money laundering.
They are based on a week of **synthetic** payments on a fictional XRPL-style ledger, valued in
US dollars. Nothing here is a real person, account or allegation.

Each case is one **alert**: a group of linked payments our model flagged together. The **risk score**
(0 to 1) ranks the alerts, riskiest first. The reasons explain what stands out.

"""

GLOSSARY = """## How to read these reports

| Term | Meaning |
|---|---|
| Risk score | How suspicious the whole alert looks, from 0 (normal) to 1 (very suspicious). Used to decide which cases to look at first |
| Model probability | How suspicious one single payment looks to our model, from 0 to 1 |
| Linked payments / burst | Payments connected to each other (the same money moving on, splitting or joining) within a few minutes |
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


def template_summary(a):
    n = len(a["tx_hashes"])
    total = sum(a["amounts_usd"])
    lines = [
        f"### {a['alert_id']} — risk {a['risk_score']:.2f}",
        "",
        f"Between {a['times'][0][11:16]} and {a['times'][-1][11:16]} UTC on {a['times'][0][:10]}, "
        f"**{n} linked payments** worth **${total:,.0f}** moved between **{len(a['accounts'])} accounts** "
        f"in **{a['minutes_total']} minutes**. It started when `{short(a['edges'][0][0])}` paid "
        f"`{short(a['edges'][0][1])}` {cite(a['tx_hashes'][0])} and ended with a payment to "
        f"`{short(a['edges'][-1][1])}` {cite(a['tx_hashes'][-1])}.",
        "",
        "**Payments:**",
    ]
    for i, h in enumerate(a["tx_hashes"]):
        s, d = a["edges"][i]
        lines.append(f"{i + 1}. {a['times'][i][11:19]} `{short(s)}` → `{short(d)}`: "
                     f"{a['amounts'][i]:,.2f} {a['assets'][i]} (${a['amounts_usd'][i]:,.0f}), "
                     f"model probability {a['probabilities'][i]:.2f} {cite(h)}")
    lines += ["", "**Why it was flagged:** " + "; ".join(a["reasons"]) + "."]
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
