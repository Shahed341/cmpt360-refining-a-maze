"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : grid_table.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 12, 2026

PURPOSE
Produce the rows of Table 1 in the report (optimal R for complete grids).

METHOD
For each complete n x m grid:
1. Build the grid and solve it with fasterAlgo.
2. Double-check the answer with is_valid_refinement.
3. Print the row:  grid | |E(M)| | optimum | spanning tree? | how found
Grids with at most 3 rows or columns are answered by Theorem 3 (the comb),
so no search is needed.

DEPENDENCIES
helpers/maze_tools.py
   full_grid            the complete n x m grid
   all_pairs_bfs        shortest distances in M
   is_valid_refinement  test the +2 condition for the answer
fasterAlgo.py
   solve_fast           the faster exact solver

USAGE
   python -m helpers.grid_table                 all grids of Table 1 (6 x 6 can take minutes)
   python -m helpers.grid_table 4x4 4x5 5x5     only the grids you list
"""

import sys
import time

from helpers.maze_tools import full_grid, is_valid_refinement, all_pairs_bfs
from fasterAlgo import solve_fast


# Grids of Table 1, used when none are given on the command line.
DEFAULT = ["2x6", "3x3", "3x7", "4x4", "4x5", "4x6", "4x7", "4x8", "5x5", "5x6", "6x6"]


# Command-line entry point

def main():
    """Solve each requested complete grid and print one table row per grid."""
    grids = sys.argv[1:] or DEFAULT
    print(f"{'grid':6} {'|E(M)|':>6}  {'optimum':10} {'tree?':6} how found")

    for g in grids:
        n, m = map(int, g.lower().split("x"))
        V, E = full_grid(n, m)
        N = len(V)

        t0 = time.perf_counter()
        kept, _ = solve_fast(V, E, m, n)
        elapsed = time.perf_counter() - t0

        # Double-check the answer.
        assert is_valid_refinement(V, kept, all_pairs_bfs(V, E))

        # Size of R relative to N: N-1 means R is a spanning tree.
        k = len(kept) - N
        rel = "N-1" if k == -1 else "N" if k == 0 else f"N+{k}"
        how = "Theorem 3" if min(n, m) <= 3 else f"search, {elapsed:.2f} s"
        print(f"{n}x{m:<4} {len(E):>6}  {len(kept):>3} = {rel:5} "
              f"{'yes' if k == -1 else 'no':6} {how}", flush=True)


if __name__ == "__main__":
    main()
