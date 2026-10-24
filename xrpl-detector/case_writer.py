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
        f.write("# Case summaries\n\n" + "\n\n---\n\n".join(s["summary"] for s in summaries))


if __name__ == "__main__":
    save(write(json.load(open(config.RANKED_JSON))))
    print(f"summaries -> {config.SUMMARIES_MD}")
