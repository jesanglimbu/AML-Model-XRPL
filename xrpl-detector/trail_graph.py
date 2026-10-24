"""TRAIL PICTURES.  Owner: person B

Input : outputs/ranked_alerts.json
Output: outputs/graphs/A001.png ...   <- put these on the slides

Starter: draws the alert's accounts and payments (arrows = money, labels = USD + time,
darker red = higher model probability).
TODO: label the shape (chain/fan-out/cycle), mark the first sender and last receiver.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

import config


def short(addr):
    return addr[:5] + "…" + addr[-3:]


def draw_trail(alert, out_dir=config.GRAPH_DIR):
    G = nx.MultiDiGraph()
    for (s, d), usd, t, p in zip(alert["edges"], alert["amounts_usd"], alert["times"], alert["probabilities"]):
        G.add_edge(s, d, label=f"${usd:,.0f} {t[11:16]}", p=p)
    first_src = alert["edges"][0][0]
    pos = nx.spring_layout(nx.DiGraph(G), seed=2, k=1.2)
    plt.figure(figsize=(8, 6))
    colours = ["#2446a8" if n == first_src else "#c2362b" for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=colours, node_size=700, alpha=0.9)
    nx.draw_networkx_labels(G, {n: (x, y + 0.09) for n, (x, y) in pos.items()},
                            labels={n: short(n) for n in G.nodes}, font_size=8, font_weight="bold")
    simple = nx.DiGraph(G)
    nx.draw_networkx_edges(simple, pos, arrows=True, arrowsize=16, width=1.5, node_size=700,
                           edge_color="#555", connectionstyle="arc3,rad=0.08")
    labels = {}
    for s, d, data in G.edges(data=True):
        labels[(s, d)] = (labels.get((s, d), "") + "\n" + data["label"]).strip()
    nx.draw_networkx_edge_labels(simple, pos, edge_labels=labels, font_size=7)
    plt.title(f"{alert['alert_id']}: {len(alert['tx_hashes'])} payments, {len(alert['accounts'])} accounts, "
              f"{alert['minutes_total']} min" + (f" | risk {alert['risk_score']:.2f}" if "risk_score" in alert else ""))
    plt.axis("off")
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    out = f"{out_dir}/{alert['alert_id']}.png"
    plt.savefig(out, dpi=150)
    plt.close()
    return out


if __name__ == "__main__":
    for a in json.load(open(config.RANKED_JSON))[:config.TOP_N_SUMMARIES]:
        print("drew", draw_trail(a))
