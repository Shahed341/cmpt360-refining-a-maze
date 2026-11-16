"""
experiments.py - runs the algorithms on random mazes and saves the results (Section 5).

Three algorithms are compared:
    baseline            backtracking with BFS checks (baseline.py)
    fasterAlgo-noPack   fasterAlgo with idea (5), the square-packing bound, switched off
    fasterAlgo          the full faster algorithm
Comparing the last two shows how much idea (5) alone helps.

Each run happens in its own process with a time limit, so a slow run is stopped
instead of freezing the whole experiment. 5 random mazes (seeds 0-4) per setting.

Experiment A (results/exp_size.csv):  grid size grows, loop probability 0.3
Experiment B (results/exp_loops.csv): 5 x 5 grid, loop probability 0.0, 0.1, ..., 1.0

Usage:
    python experiments.py            30 s limit per run (takes about 30-45 minutes)
    python experiments.py 10         10 s limit per run (faster, less data)
    python experiments.py 2 --quick  small sizes only, to test that everything works
"""
import csv
import sys
import time
import multiprocessing as mp
from maze_tools import random_maze
from baseline import solve_baseline
from fasterAlgo import solve_fast

ALGOS = ("baseline", "fasterAlgo-noPack", "fasterAlgo")
FIELDS = ["algo", "rows", "cols", "V", "E", "loops", "loop_prob", "seed",
          "solved", "opt", "checks", "seconds"]


def _worker(algo, n, m, p, seed, q):
    """Runs one algorithm on one maze (inside its own process) and reports back."""
    V, E = random_maze(n, m, p, seed)
    t0 = time.perf_counter()
    if algo == "baseline":
        kept, checks = solve_baseline(V, E)
    else:
        kept, checks = solve_fast(V, E, m, n, packing=(algo == "fasterAlgo"))
    q.put((len(kept), checks, time.perf_counter() - t0))


def run(algo, n, m, p, seed, limit):
    """One timed run. Returns a result row; solved = 0 if it hit the time limit."""
    V, E = random_maze(n, m, p, seed)
    q = mp.Queue()
    proc = mp.Process(target=_worker, args=(algo, n, m, p, seed, q))
    proc.start()
    proc.join(limit)
    row = dict(algo=algo, rows=n, cols=m, V=len(V), E=len(E), loops=len(E) - len(V) + 1,
               loop_prob=p, seed=seed)
    if proc.is_alive():                       # still running after the limit -> stop it
        proc.terminate()
        proc.join()
        row.update(solved=0, opt="", checks="", seconds=limit)
    else:
        opt, checks, sec = q.get()
        row.update(solved=1, opt=opt, checks=checks, seconds=round(sec, 4))
    return row


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    limit = float(args[0]) if args else 30
    quick = "--quick" in sys.argv
    seeds = range(5)

    sizes = [(3, 3), (3, 4), (4, 4), (4, 5), (5, 5), (5, 6), (6, 6), (6, 7), (7, 7), (8, 8),
             (9, 9), (10, 10), (12, 12), (14, 14), (16, 16), (20, 20)]
    probs = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    if quick:
        sizes, probs = sizes[:4], [0.0, 0.5, 1.0]

    # ---- Experiment A: growing size, loop probability 0.3
    with open("results/exp_size.csv", "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for algo in ALGOS:
            for n, m in sizes:
                rows = [run(algo, n, m, 0.3, s, limit) for s in seeds]
                for r in rows:
                    w.writerow(r)
                f.flush()
                solved = sum(r["solved"] for r in rows)
                print(f"A  {algo:18} {n}x{m:<3} solved {solved}/5", flush=True)
                if solved == 0:
                    break                      # bigger sizes would time out too

    # ---- Experiment B: 5 x 5 grid, more and more loops
    with open("results/exp_loops.csv", "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for algo in ALGOS:
            for p in probs:
                rows = [run(algo, 5, 5, p, s, limit) for s in seeds]
                for r in rows:
                    w.writerow(r)
                f.flush()
                solved = sum(r["solved"] for r in rows)
                print(f"B  {algo:18} p={p:<4} solved {solved}/5", flush=True)
    print("done: results/exp_size.csv and results/exp_loops.csv")


if __name__ == "__main__":
    main()
