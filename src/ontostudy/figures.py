"""Figures for docs/results, drawn from the CSVs only.

    python -m ontostudy.figures            # writes docs/results/fig*.png (+ .pdf)

fig1_hops      each question's hop cost relative to mid, main run, largest scale
fig2_scaling   latency against persons, log-log, six diagnostic questions, with fitted slope ± 2 SE
fig3_memory    resident size (Python engine) and on-disk size (Kùzu) against persons
fig4_followups Q17–Q19 hops under the three runs (main, indexed, skewed) and records touched per write

Colour is Okabe–Ito (blue, vermillion, bluish green) with a distinct marker per
schema so no series is identified by colour alone. Log axes are labelled as such.
"""

from __future__ import annotations

import csv
import math
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .report import DIAG, load_bench, slope

ROOT = pathlib.Path(__file__).resolve().parents[2]
RES = ROOT / "docs" / "results"
COLOR = {"flat": "#0072B2", "mid": "#D55E00", "normalized": "#009E73", "flat_indexed": "#0072B2"}
MARK = {"flat": "o", "mid": "s", "normalized": "^", "flat_indexed": "D"}
FILL = {"flat_indexed": "none"}
STYLE = {"font.family": "sans-serif", "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7.5,
         "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#dddddd", "grid.linewidth": 0.5,
         "axes.axisbelow": True, "figure.dpi": 100, "savefig.dpi": 300, "lines.linewidth": 1.2, "lines.markersize": 4}
MM = 1 / 25.4


def question_kind():
    import re
    out = {}
    for line in (ROOT / "src/ontostudy/queries/QUESTIONS.md").read_text().splitlines():
        m = re.match(r"\| (Q\d\d) \| (.+?) \| (.+?) \|", line)
        if m: out[m.group(1)] = (m.group(2), m.group(3))
    return out


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(RES / f"{name}.{ext}", bbox_inches=None)
    plt.close(fig)
    print("wrote", name)


def series_kw(s):
    return dict(color=COLOR[s], marker=MARK[s], markerfacecolor=FILL.get(s, COLOR[s]), label=s, linestyle="none")


def fig1(R):
    n = R["scales"][-1]; B = R["B"]; qs = R["queries"]
    fig, ax = plt.subplots(figsize=(170 * MM, 110 * MM), layout="constrained")
    ys = list(range(len(qs)))[::-1]
    for s in R["schemas"]:
        xs = [int(B[(n, s, q)]["hops"]) / int(B[(n, "mid", q)]["hops"]) for q in qs]
        ax.plot(xs, ys, **series_kw(s))
    ax.axvline(1, color="black", linewidth=0.8)
    ax.set_xscale("log"); ax.set_yticks(ys); ax.set_yticklabels(qs)
    ax.set_xlabel(f"hops relative to the mid schema, log scale (n = {n:,} persons)")
    ax.set_title("Each question's traversal cost relative to mid", loc="left")
    ax.legend(loc="lower right", frameon=False)
    ax.grid(axis="y", visible=False)
    save(fig, "fig1_hops")


def fig2(R):
    from matplotlib.ticker import LogLocator, NullFormatter
    qk = question_kind()
    fig, axes = plt.subplots(2, 3, figsize=(170 * MM, 100 * MM), layout="constrained", sharex=True)
    for ax, q in zip(axes.flat, DIAG):
        ends = []
        for s in R["schemas"]:
            ys = [float(R["B"][(n, s, q)]["seconds"]) * 1000 for n in R["scales"]]
            b, se = slope(R, s, q)
            kw = series_kw(s); kw["linestyle"] = "-"
            ax.plot(R["scales"], ys, **kw)
            ends.append((ys[-1], s, f"{b:.2f}" + (f" ± {2 * se:.2f}" if not math.isnan(se) else "")))
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10, numticks=6)); ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(f"{q}: {qk[q][1]}", loc="left")
        ax.set_xlim(R["scales"][0] / 1.3, R["scales"][-1] * 4)   # room for the slope labels
        # slope labels at the line ends, nudged apart in axes coordinates
        lo, hi = ax.get_ylim(); frac = lambda y: (math.log(y) - math.log(lo)) / (math.log(hi) - math.log(lo))
        pos = sorted((frac(y), s, t) for y, s, t in ends); out = []
        for f, s, t in pos:
            if out and f - out[-1][0] < 0.09: f = out[-1][0] + 0.09
            out.append((f, s, t))
        for f, s, t in out:
            ax.annotate(t, xy=(R["scales"][-1], math.exp(math.log(lo) + f * (math.log(hi) - math.log(lo)))), xytext=(5, 0),
                        textcoords="offset points", fontsize=6.5, color=COLOR[s], va="center")
    for ax in axes[1]: ax.set_xlabel("persons, log scale")
    for ax in axes[:, 0]: ax.set_ylabel("ms per query, log scale")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=3, frameon=False)
    fig.suptitle(f"Latency against scale; the number at each line end is the fitted log-log slope over {len(R['scales'])} scales, ± 2 SE", x=0.01, ha="left", fontsize=9)
    save(fig, "fig2_scaling")


def fig3(R, K):
    fig, axes = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM), layout="constrained")
    for ax, run, title, ylabel in ((axes[0], R, "Python engine, resident size", "MB, log scale"), (axes[1], K, "Kùzu, on-disk size", "MB, log scale")):
        if not run: ax.set_visible(False); continue
        for s in run["schemas"]:
            ys = [float(run["sizes"][(n, s)]["mbytes"]) for n in run["scales"]]
            kw = series_kw(s); kw["linestyle"] = "-"
            ax.plot(run["scales"], ys, **kw)
        n = run["scales"][-1]
        ratio = float(run["sizes"][(n, "normalized")]["mbytes"]) / float(run["sizes"][(n, "mid")]["mbytes"])
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(f"{title}; normalized / mid = {ratio:.2f} at {n:,}", loc="left")
        ax.set_xlabel("persons, log scale"); ax.set_ylabel(ylabel); ax.legend(frameon=False)
    save(fig, "fig3_memory")


def fig4(runs, writes):
    fig, axes = plt.subplots(1, 2, figsize=(170 * MM, 75 * MM), layout="constrained", width_ratios=[3, 2])
    # (a) reverse lookups under the three runs, grouped by question
    ax = axes[0]
    runs = {k: v for k, v in runs.items() if v}
    ticks, ticklabels = [], []
    for gi, q in enumerate(("Q17", "Q18", "Q19")):
        for ri, (tag, R) in enumerate(runs.items()):
            x = gi * (len(runs) + 1) + ri; n = R["scales"][-1]
            for s in R["schemas"]:
                if s == "normalized": continue
                ax.plot(x, int(R["B"][(n, s, q)]["hops"]), **series_kw(s))
            ticks.append(x); ticklabels.append({"main": "main", "indexed": "+index", "skew": "skew"}[tag])
        ax.text(gi * (len(runs) + 1) + (len(runs) - 1) / 2, 1.02, q, transform=ax.get_xaxis_transform(), ha="center", fontsize=8)
    ax.set_yscale("log"); ax.set_xticks(ticks); ax.set_xticklabels(ticklabels, fontsize=7)
    ax.set_ylabel("hops per query at 10,000 persons, log scale"); ax.set_title("Reverse lookups under the three runs", loc="left", pad=14)
    h, l = ax.get_legend_handles_labels(); seen = {}; [seen.setdefault(b, a) for a, b in zip(h, l)]
    ax.legend(seen.values(), seen.keys(), frameon=False, loc="lower left", ncol=3, bbox_to_anchor=(0, -0.42))
    # (b) writes
    ax = axes[1]
    if writes:
        n = max(int(r["scale"]) for r in writes); W = [r for r in writes if int(r["scale"]) == n]
        ups = list(dict.fromkeys(r["update"] for r in W)); schemas = list(dict.fromkeys(r["schema"] for r in W))
        for i, s in enumerate(schemas):
            ys = [int(next(r["records"] for r in W if r["schema"] == s and r["update"] == u)) for u in ups]
            ax.plot([k + (i - 1.5) * 0.18 for k in range(len(ups))], ys, **series_kw(s))
        ax.set_yscale("log"); ax.set_xticks(range(len(ups))); ax.set_xticklabels([u.replace("_", "\n") for u in ups], fontsize=7)
        ax.set_ylabel(f"records touched per update, log scale"); ax.set_title(f"The write path, {n:,} persons", loc="left", pad=14)
        ax.legend(frameon=False, loc="lower left", ncol=2, bbox_to_anchor=(0, -0.42))
    save(fig, "fig4_followups")


def main() -> int:
    plt.rcParams.update(STYLE)
    R = load_bench("bench.csv"); K = load_bench("bench_kuzu.csv")
    fig1(R); fig2(R); fig3(R, K)
    runs = {"main": R, "indexed": load_bench("bench_indexed.csv"), "skew": load_bench("bench_skew.csv")}
    writes = list(csv.DictReader((RES / "writes.csv").open())) if (RES / "writes.csv").exists() else []
    fig4(runs, writes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
