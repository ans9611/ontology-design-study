"""Generate every table in docs/results/RESULTS.md from the CSVs.

    python -m ontostudy.report

Tables are written between `<!-- table:NAME -->` and `<!-- /table -->` markers;
prose outside the markers is left alone. If a marker's CSV is missing the block
is left as it is. No number in a table is typed by hand.
"""

from __future__ import annotations

import csv
import math
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RES = ROOT / "docs" / "results"

DIAG = ["Q02", "Q11", "Q13", "Q17", "Q18", "Q19"]   # forward reads, path, reverse lookups


def load_bench(name):
    p = RES / name
    if not p.exists():
        return None
    rows = list(csv.DictReader(p.open()))
    B = {(int(r["scale"]), r["schema"], r["query"]): r for r in rows}
    scales = sorted({int(r["scale"]) for r in rows})
    schemas = list(dict.fromkeys(r["schema"] for r in rows))
    queries = sorted({r["query"] for r in rows})
    sizes_name = name.replace("bench", "sizes")
    sizes = {(int(r["scale"]), r["schema"]): r for r in csv.DictReader((RES / sizes_name).open())} if (RES / sizes_name).exists() else {}
    return {"B": B, "scales": scales, "schemas": schemas, "queries": queries, "sizes": sizes, "name": name}


def ols(xs, ys):
    """slope, standard error of the slope."""
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    if n <= 2:
        return b, float("nan")
    resid = sum((y - (my + b * (x - mx))) ** 2 for x, y in zip(xs, ys))
    return b, math.sqrt(resid / (n - 2) / sxx)


def slope(R, s, q, key="seconds"):
    pts = [(math.log(n), math.log(float(R["B"][(n, s, q)][key]))) for n in R["scales"] if (n, s, q) in R["B"]]
    return ols([x for x, _ in pts], [y for _, y in pts])


def slope_ci(R, s, q, boots=200, seed=0):
    """Bootstrap CI over the recorded repeats, when the run stored them; else None."""
    import random
    rng = random.Random(seed)
    runs = {n: [float(x) for x in R["B"][(n, s, q)].get("runs", "").split(";") if x] for n in R["scales"]}
    if not all(runs.values()):
        return None
    bs = []
    for _ in range(boots):
        xs = [math.log(n) for n in R["scales"]]
        ys = [math.log(min(rng.choice(v) for _ in range(len(v)))) for v in runs.values()]
        bs.append(ols(xs, ys)[0])
    bs.sort()
    return bs[int(0.025 * boots)], bs[int(0.975 * boots)]


def f(x, d=2):
    return f"{x:,.{d}f}"


def ols_multi(X, y):
    """Least squares for a few regressors: returns coefficients (last is the intercept) and R²."""
    import numpy as np
    A = np.column_stack([np.array(X, dtype=float), np.ones(len(y))])
    coef, *_ = np.linalg.lstsq(A, np.array(y, dtype=float), rcond=None)
    pred = A @ coef; yv = np.array(y, dtype=float)
    r2 = 1 - ((yv - pred) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
    return coef.tolist(), float(r2)


def cost_model():
    """log(ms) = a·log(1 + random accesses) + b·log(1 + scanned records) + c, fitted per engine.

    Counts come from the Python engine's bench.csv (they are properties of the schema, not
    the engine); the Kùzu fit uses those counts with Kùzu's own times on the rows both runs share.
    Returns None until bench.csv carries the `scans` column.
    """
    R = load_bench("bench.csv")
    if not R or "scans" not in next(iter(R["B"].values())):
        return None
    def xs(row):
        h, sc = int(row["hops"]), int(row["scans"])
        return [math.log1p(h - sc), math.log1p(sc)]
    fits = {}
    X = [xs(r) for r in R["B"].values()]; y = [math.log(float(r["seconds"]) * 1000) for r in R["B"].values()]
    (a, b, c), r2 = ols_multi(X, y); fits["python"] = {"a": a, "b": b, "c": c, "r2": r2, "n": len(y)}
    K = load_bench("bench_kuzu.csv")
    if K:
        X, y = [], []
        for key, row in K["B"].items():
            if key in R["B"]:
                X.append(xs(R["B"][key])); y.append(math.log(float(row["seconds"]) * 1000))
        if len(y) > 6:
            (a, b, c), r2 = ols_multi(X, y); fits["kuzu"] = {"a": a, "b": b, "c": c, "r2": r2, "n": len(y)}
    return fits


def cost_model_table(fits):
    out = ["| engine | a: random access | b: sequential scan | c: fixed (log ms) | R² | rows |", "|---|---|---|---|---|---|"]
    for eng, m in fits.items():
        out.append(f"| {eng} | {m['a']:.2f} | {m['b']:.2f} | {m['c']:.2f} | {m['r2']:.2f} | {m['n']} |")
    return ("Fit of log(ms per query) = a·log(1 + random accesses) + b·log(1 + scanned records) + c. Random accesses are edge traversals and "
            "index hits (pointer chasing); scanned records are nodes visited by a full scan of a type. Counts are the schema's, taken from the "
            "Python engine; each engine contributes its own times.\n\n" + "\n".join(out))


REF_SCALE = 10000   # the one scale every run shares; headline numbers are reported here


def ref_scale(R):
    return REF_SCALE if REF_SCALE in R["scales"] else R["scales"][-1]


def boot_median(values, boots=2000, seed=0):
    """Median with a 95% bootstrap interval over the twenty queries."""
    import random
    rng = random.Random(seed); v = list(values); meds = []
    for _ in range(boots):
        meds.append(statistics.median(rng.choice(v) for _ in v))
    meds.sort()
    return statistics.median(v), meds[int(0.025 * boots)], meds[int(0.975 * boots)]


def headline(R):
    n = ref_scale(R); B = R["B"]; qs = R["queries"]; S = R["schemas"]
    hop = lambda s, q: int(B[(n, s, q)]["hops"])
    ms = lambda s, q: float(B[(n, s, q)]["seconds"])
    out = ["| | " + " | ".join(S) + " |", "|---|" + "---|" * len(S)]
    if "mid" in S:
        def cell(vals):
            m, lo, hi = boot_median(vals); return f"{f(m)} [{f(lo)}, {f(hi)}]"
        out.append(f"| median hop ratio to mid, n={n:,} [95% CI over queries] | " + " | ".join(cell([hop(s, q) / hop("mid", q) for q in qs]) for s in S) + " |")
        out.append(f"| median latency ratio to mid, n={n:,} [95% CI] | " + " | ".join(cell([ms(s, q) / ms("mid", q) for q in qs]) for s in S) + " |")
    if R["sizes"]:
        out.append(f"| size at n={n:,} | " + " | ".join(f"{float(R['sizes'][(n, s)]['mbytes']):,.0f} MB" for s in S) + " |")
        out.append(f"| build time at n={n:,} | " + " | ".join(f"{float(R['sizes'][(n, s)]['build_seconds']):.1f} s" for s in S) + " |")
    out.append("| queries within 20% of the fastest | " + " | ".join(str(sum(ms(s, q) <= 1.2 * min(ms(x, q) for x in S) for q in qs)) for s in S) + " |")
    steep = {s: [q for q in qs if slope(R, s, q)[0] > 0.5] for s in S}
    out.append("| queries with latency exponent > 0.5 | " + " | ".join(f"{len(steep[s])}" + (f" ({', '.join(steep[s])})" if steep[s] else "") for s in S) + " |")
    return "\n".join(out)


def per_query(R):
    n = ref_scale(R); B = R["B"]; S = R["schemas"]
    head = "| query | " + " | ".join(f"hops {s}" for s in S) + " | " + " | ".join(f"ms {s}" for s in S) + " | " + " | ".join(f"exp {s}" for s in S) + " |"
    out = [head, "|---|" + "---|" * (3 * len(S))]
    for q in R["queries"]:
        cells = [f"{int(B[(n, s, q)]['hops']):,}" if "hops" in B[(n, s, q)] else "" for s in S]
        cells += [f"{float(B[(n, s, q)]['seconds']) * 1000:.3f}" for s in S]
        for s in S:
            b, se = slope(R, s, q)
            cells.append(f"{b:.2f}" + (f" ± {2 * se:.2f}" if not math.isnan(se) else ""))
        out.append(f"| {q} | " + " | ".join(cells) + " |")
    note = ("exp = slope of log(latency) against log(persons) over " + " / ".join(f"{n:,}" for n in R["scales"]) +
            ("; ± is two standard errors of the fit" if len(R["scales"]) > 2 else "") + ".")
    return note + "\n\n" + "\n".join(out)


def diagnostic(R, key="hops"):
    """The six diagnostic queries, one row each, hops (or ms) and slope per schema."""
    n = ref_scale(R); B = R["B"]; S = R["schemas"]
    label = "hops" if key == "hops" else "ms"
    out = ["| query | " + " | ".join(f"{label} {s}" for s in S) + " | " + " | ".join(f"exp {s}" for s in S) + " |", "|---|" + "---|" * (2 * len(S))]
    for q in [q for q in DIAG if q in R["queries"]]:
        cells = [f"{int(B[(n, s, q)]['hops']):,}" if key == "hops" else f"{float(B[(n, s, q)]['seconds']) * 1000:.3f}" for s in S]
        cells += [f"{slope(R, s, q)[0]:.2f}" for s in S]
        out.append(f"| {q} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def sizes_table(R):
    S = R["schemas"]
    out = ["| persons | " + " | ".join(f"{s} MB" for s in S) + " |", "|---|" + "---|" * len(S)]
    for n in R["scales"]:
        out.append(f"| {n:,} | " + " | ".join(f"{float(R['sizes'][(n, s)]['mbytes']):,.1f}" for s in S) + " |")
    return "\n".join(out)


def writes_table():
    p = RES / "writes.csv"
    if not p.exists():
        return None
    rows = list(csv.DictReader(p.open())); n = max(int(r["scale"]) for r in rows)
    S = list(dict.fromkeys(r["schema"] for r in rows)); U = list(dict.fromkeys(r["update"] for r in rows))
    W = {(r["schema"], r["update"]): r for r in rows if int(r["scale"]) == n}
    out = [f"Records touched per update and microseconds per update, n = {n:,}, best of k.", "",
           "| update | " + " | ".join(f"{s} records" for s in S) + " | " + " | ".join(f"{s} µs" for s in S) + " |", "|---|" + "---|" * (2 * len(S))]
    for u in U:
        out.append(f"| {u} | " + " | ".join(W[(s, u)]["records"] for s in S) + " | " + " | ".join(f"{float(W[(s, u)]['seconds']) * 1e6:.1f}" for s in S) + " |")
    return "\n".join(out)


def build_blocks():
    blocks = {}
    R = load_bench("bench.csv")
    if R:
        blocks["headline"] = headline(R)
        blocks["per-query"] = per_query(R)
        blocks["sizes"] = sizes_table(R)
    for tag, name in (("indexed", "bench_indexed.csv"), ("skew", "bench_skew.csv")):
        Rx = load_bench(name)
        if Rx:
            blocks[f"{tag}-headline"] = headline(Rx)
            blocks[f"{tag}-diagnostic"] = diagnostic(Rx)
    Rk = load_bench("bench_kuzu.csv")
    if Rk:
        blocks["kuzu-diagnostic"] = diagnostic(Rk, key="ms")
        blocks["kuzu-sizes"] = sizes_table(Rk)
    w = writes_table()
    if w:
        blocks["writes"] = w
    cm = cost_model()
    if cm:
        blocks["cost-model"] = cost_model_table(cm)
    return blocks


def render(text, blocks):
    def sub(m):
        name = m.group(1)
        return f"<!-- table:{name} -->\n{blocks[name]}\n<!-- /table -->" if name in blocks else m.group(0)
    return re.sub(r"<!-- table:([\w-]+) -->\n.*?<!-- /table -->", sub, text, flags=re.S)


def main() -> int:
    p = RES / "RESULTS.md"
    blocks = build_blocks()
    new = render(p.read_text(), blocks)
    p.write_text(new)
    print("tables:", ", ".join(sorted(blocks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
