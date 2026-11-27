"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : summarize.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 16, 2026

PURPOSE
Turn the experiment results into the numbers used in Section 5.

OUTPUT
   - Table 2: the largest grid size each algorithm solved in all 5 runs
   - how many times fewer checks, and how much faster, each fasterAlgo
     version is than the baseline (runs that both finished)
   - the most loops each algorithm solved, and the fewest loops at which it
     timed out
   - Experiment B: runs solved per loop probability

DEPENDENCIES
results/exp_size.csv and results/exp_loops.csv, written by experiments.py.
Python standard library only (csv, statistics).

USAGE
   python -m helpers.summarize      (after python -m helpers.experiments)
"""

import csv
import statistics


ALGOS = ("baseline", "fasterAlgo-noPack", "fasterAlgo")


# Helpers

def load(path):
    """
    Read a results CSV file.

    Parameters
    ----------
    path : str
        Path of the CSV file.

    Returns
    -------
    list of dict
        One dict per row; every value is a string.
    """
    with open(path) as f:
        return list(csv.DictReader(f))


# Command-line entry point

def main():
    """Print Table 2 and the Section 5 numbers."""
    A, B = load("results/exp_size.csv"), load("results/exp_loops.csv")

    # Table 2: largest size where all 5 runs finished.
    print("Table 2: largest size solved in all 5 runs (loop probability 0.3)")
    print(f"{'algorithm':20} {'size':8} {'median time':>12} {'median checks':>14}")
    for algo in ALGOS:
        sizes = sorted({(int(r["rows"]), int(r["cols"])) for r in A if r["algo"] == algo},
                       key=lambda s: s[0] * s[1])
        best = None
        for n, m in sizes:
            runs = [r for r in A if r["algo"] == algo and (int(r["rows"]), int(r["cols"])) == (n, m)]
            if all(r["solved"] == "1" for r in runs):
                best = (n, m, runs)
        if best:
            n, m, runs = best
            t = statistics.median(float(r["seconds"]) for r in runs)
            c = statistics.median(int(r["checks"]) for r in runs)
            print(f"{algo:20} {n}x{m:<6} {t:>10.3f} s {c:>14,}")

    # Speed-up over the baseline, on the same maze, when both runs finished.
    print("\nCompared with the baseline (runs that both finished):")
    for algo in ("fasterAlgo-noPack", "fasterAlgo"):
        rc, rt = [], []                       # ratios of checks and of times
        for data, key in ((A, ("rows", "cols", "seed")), (B, ("loop_prob", "seed"))):
            for b in [r for r in data if r["algo"] == "baseline" and r["solved"] == "1"]:
                # The matching run of this algorithm on the same maze.
                f = [r for r in data if r["algo"] == algo and all(r[k] == b[k] for k in key)]
                if f and f[0]["solved"] == "1" and int(f[0]["checks"]) > 0:
                    rc.append(int(b["checks"]) / int(f[0]["checks"]))
                    rt.append(float(b["seconds"]) / max(float(f[0]["seconds"]), 1e-4))
        if rc:
            print(f"  {algo:18}: median {statistics.median(rc):.0f}x fewer checks, "
                  f"{statistics.median(rt):.1f}x faster  ({len(rc)} runs)")

    # Most loops solved and fewest loops at a timeout, over both experiments.
    print("\nLoops (both experiments):")
    for algo in ALGOS:
        ok = [int(r["loops"]) for r in A + B if r["algo"] == algo and r["solved"] == "1"]
        bad = [int(r["loops"]) for r in A + B if r["algo"] == algo and r["solved"] == "0"]
        msg = f"  {algo:18}: solved up to {max(ok)} loops"
        msg += f", first timeout at {min(bad)} loops" if bad else ", no timeouts"
        print(msg)

    # Experiment B: how many of the 5 runs finished at each loop probability.
    print("\nExperiment B (5 x 5): runs solved per loop probability")
    probs = sorted({r["loop_prob"] for r in B}, key=float)
    short = {"baseline": "baseline", "fasterAlgo-noPack": "no (5)", "fasterAlgo": "faster"}
    print("  p        " + "  ".join(f"{p:>4}" for p in probs))
    for algo in ALGOS:
        cells = [sum(r["solved"] == "1" for r in B if r["algo"] == algo and r["loop_prob"] == p)
                 for p in probs]
        print(f"  {short[algo]:8} " + "  ".join(f"{c}/5" for c in cells))


if __name__ == "__main__":
    main()
