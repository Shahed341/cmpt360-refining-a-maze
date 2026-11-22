"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : experiments.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 16, 2026

PURPOSE
Run the algorithms on random mazes and save the results used in Section 5.

Three algorithms are compared:
   baseline            backtracking with BFS checks (baseline.py)
   fasterAlgo-noPack   fasterAlgo with idea (5), the square-packing bound, off
   fasterAlgo          the full faster algorithm
Comparing the last two shows how much idea (5) alone helps.

METHOD
1. Each run happens in its own process with a time limit, so a slow run is
   stopped instead of freezing the whole experiment.
2. 5 random mazes (seeds 0-4) per setting.
3. Experiment A (results/exp_size.csv):  grid size grows, loop probability 0.3.
   Once an algorithm solves none of the 5 mazes at a size, its larger sizes
   are skipped.
4. Experiment B (results/exp_loops.csv): 5 x 5 grid, loop probability
   0.0, 0.1, ..., 1.0.

DEPENDENCIES
maze_tools.py
   random_maze      a random connected maze
baseline.py
   solve_baseline   the exact baseline solver
fasterAlgo.py
   solve_fast       the faster exact solver

OUTPUT
One CSV row per run with the columns in FIELDS. solved = 0 means the run hit
the time limit; then opt and checks are empty and seconds = the limit.

USAGE
   python experiments.py              30 s limit per run (about 30-45 minutes)
   python experiments.py 10           10 s limit per run (faster, less data)
   python experiments.py 2 --quick    small sizes only, to test that everything works
"""

import csv
import sys
import time
import multiprocessing as mp

from maze_tools import random_maze
from baseline import solve_baseline
from fasterAlgo import solve_fast


# Algorithm names and CSV columns.
ALGOS = ("baseline", "fasterAlgo-noPack", "fasterAlgo")
FIELDS = ["algo", "rows", "cols", "V", "E", "loops", "loop_prob", "seed",
          "solved", "opt", "checks", "seconds"]


# Running one algorithm on one maze

def _worker(algo, n, m, p, seed, q):
    """
    Run one algorithm on one maze inside its own process and report back.

    Parameters
    ----------
    algo : str
        One of ALGOS.
    n, m : int
        Grid size.
    p : float
        Loop probability for random_maze.
    seed : int
        Random seed for random_maze.
    q : multiprocessing.Queue
        Receives (number of kept corridors, checks, seconds).
    """
    V, E = random_maze(n, m, p, seed)
    t0 = time.perf_counter()
    if algo == "baseline":
        kept, checks = solve_baseline(V, E)
    else:
        kept, checks = solve_fast(V, E, m, n, packing=(algo == "fasterAlgo"))
    q.put((len(kept), checks, time.perf_counter() - t0))


def run(algo, n, m, p, seed, limit):
    """
    One timed run in a separate process.

    Parameters
    ----------
    algo, n, m, p, seed :
        As in _worker.
    limit : float
        Time limit in seconds.

    Returns
    -------
    dict
        One result row with the keys in FIELDS; solved = 0 if the run hit
        the time limit.
    """
    V, E = random_maze(n, m, p, seed)
    q = mp.Queue()
    proc = mp.Process(target=_worker, args=(algo, n, m, p, seed, q))
    proc.start()
    proc.join(limit)

    row = dict(algo=algo, rows=n, cols=m, V=len(V), E=len(E), loops=len(E) - len(V) + 1,
               loop_prob=p, seed=seed)

    if proc.is_alive():
        # Still running after the limit -> stop it and record a timeout.
        proc.terminate()
        proc.join()
        row.update(solved=0, opt="", checks="", seconds=limit)
    else:
        opt, checks, sec = q.get()
        row.update(solved=1, opt=opt, checks=checks, seconds=round(sec, 4))
    return row


# Command-line entry point

def main():
    """Run Experiments A and B and write their CSV files."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    limit = float(args[0]) if args else 30
    quick = "--quick" in sys.argv
    seeds = range(5)

    sizes = [(3, 3), (3, 4), (4, 4), (4, 5), (5, 5), (5, 6), (6, 6), (6, 7), (7, 7), (8, 8),
             (9, 9), (10, 10), (12, 12), (14, 14), (16, 16), (20, 20)]
    probs = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    if quick:
        sizes, probs = sizes[:4], [0.0, 0.5, 1.0]

    # Experiment A: growing size, loop probability 0.3.
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

    # Experiment B: 5 x 5 grid, more and more loops.
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
