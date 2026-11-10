"""
baseline.py - exact baseline algorithm for "Refining a Maze" (CMPT 360, Option 1).

Goal: remove as many corridors as possible from the maze M, so that in what is left (R)
every trip is at most 2 steps longer than in M.

Idea (brute force with backtracking):
    Try sets of corridors to remove, adding one corridor at a time in a fixed order.
    After each addition, check the whole maze with is_valid_refinement (BFS from every point).
      - If the set is still valid, try adding more corridors to it.
      - If it is not valid, stop: adding even more corridors can never fix it,
        because removing more corridors never makes any trip shorter ("monotonicity").
    Remember the largest valid set found. Answer = M minus that set.

Small example (handout maze, 9 corridors):
    remove {(0,0)-(1,0)}      -> not valid (cuts off (0,0)) -> stop this branch
    remove {(1,0)-(1,1)}      -> valid -> try adding a second corridor:
        remove {(1,0)-(1,1), (1,0)-(2,0)} -> not valid -> stop ... (every pair fails)
    best = 1 corridor removed -> R has 8 corridors.

Time: up to 2^E sets, each checked in O(V * (V + E))  ->  O(2^E * V * E).  Exponential,
so it only works on small mazes. Space: O(V^2) for the distance table.

Usage:  python baseline.py <maze-file> [--quiet]
"""
import sys
import time
from maze_tools import read_maze, all_pairs_bfs, is_valid_refinement, edge_str


def solve_baseline(verts, edges):
    """Find the smallest valid refined maze R by trying sets of corridors to remove.

    verts, edges  the maze M (from read_maze)
    Returns (kept_edges, checks):
        kept_edges  the corridors of the best R found (it is optimal)
        checks      how many times is_valid_refinement was called (used in experiments)
    """
    dist_M = all_pairs_bfs(verts, edges)   # distances in M, computed once
    E = list(edges)                        # fixed order of corridors: E[0], E[1], ...
    best = [frozenset()]                   # largest valid removal set so far (in a list
                                           # so the inner function can change it)
    checks = [0]                           # counter of validity checks

    def search(start, removed):
        """Try to add corridors E[start], E[start+1], ... to the set 'removed'.

        'removed' is always valid when this is called. Corridors are only added
        in increasing index order, so every set is tried at most once.
        """
        # A bigger valid set than before? Remember it.
        if len(removed) > len(best[0]):
            best[0] = frozenset(removed)

        # Bound: even removing ALL remaining corridors could not beat the best -> give up.
        if len(removed) + (len(E) - start) <= len(best[0]):
            return

        for j in range(start, len(E)):
            removed.add(E[j])              # try removing corridor j as well
            checks[0] += 1
            kept = [e for e in E if e not in removed]
            if is_valid_refinement(verts, kept, dist_M):
                search(j + 1, removed)     # still valid -> try removing more
            # not valid -> no need to go deeper (monotonicity), just undo and move on
            removed.discard(E[j])          # undo, then try the next corridor instead

    search(0, set())
    kept = [e for e in E if e not in best[0]]
    return kept, checks[0]


def main():
    """Command line: read the maze file, solve it, print the result."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    n, m, verts, edges = read_maze(sys.argv[1])

    t0 = time.perf_counter()
    kept, checks = solve_baseline(verts, edges)
    t = time.perf_counter() - t0

    print(f"maze {n}x{m}: |V|={len(verts)} |E(M)|={len(edges)}")
    print(f"refined maze R: {len(kept)} edges  (deleted {len(edges) - len(kept)})")
    print(f"validity checks: {checks}   time: {t:.3f} s")
    if "--quiet" not in sys.argv:
        removed = [edge_str(e, m) for e in edges if e not in set(kept)]
        print("deleted edges:", ", ".join(removed) or "none")


if __name__ == "__main__":
    main()
