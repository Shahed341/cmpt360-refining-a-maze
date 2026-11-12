"""
grid_table.py - produces the rows of Table 1 (complete grids) in the report.

For each complete n x m grid it runs fasterAlgo, and prints:
    grid | |E(M)| | optimum | spanning tree? | how found (time)
Grids with at most 3 rows are answered by Theorem 3 (the comb), so no search is needed.

Usage:
    python grid_table.py                  all grids of Table 1 (6 x 6 can take minutes)
    python grid_table.py 4x4 4x5 5x5      only the grids you list
"""
import sys
import time
from maze_tools import full_grid, is_valid_refinement, all_pairs_bfs
from fasterAlgo import solve_fast

DEFAULT = ["2x6", "3x3", "3x7", "4x4", "4x5", "4x6", "4x7", "4x8", "5x5", "5x6", "6x6"]


def main():
    grids = sys.argv[1:] or DEFAULT
    print(f"{'grid':6} {'|E(M)|':>6}  {'optimum':10} {'tree?':6} how found")
    for g in grids:
        n, m = map(int, g.lower().split("x"))
        V, E = full_grid(n, m)
        N = len(V)
        t0 = time.perf_counter()
        kept, _ = solve_fast(V, E, m, n)
        t = time.perf_counter() - t0
        assert is_valid_refinement(V, kept, all_pairs_bfs(V, E))   # double-check the answer
        k = len(kept) - N
        rel = "N-1" if k == -1 else "N" if k == 0 else f"N+{k}"
        how = "Theorem 3" if min(n, m) <= 3 else f"search, {t:.2f} s"
        print(f"{n}x{m:<4} {len(E):>6}  {len(kept):>3} = {rel:5} {'yes' if k == -1 else 'no':6} {how}", flush=True)


if __name__ == "__main__":
    main()
