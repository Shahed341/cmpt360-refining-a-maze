"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : baseline.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 9, 2026

PURPOSE
Exact baseline algorithm (brute force with backtracking).

Given a maze M (a connected subgraph of an n x m grid), find a refined maze
R, a subgraph of M with the fewest corridors (edges), such that

       d_R(u, v) <= d_M(u, v) + 2        for every pair of points u, v.

In words: remove as many corridors as possible, as long as no trip between
two points gets more than 2 steps longer.

METHOD
1. Compute all shortest distances in M once (BFS from every point).
2. Build sets of corridors to remove, adding one corridor at a time in a
   fixed order, so each set is tried at most once.
3. After each addition, check the whole maze with a BFS from every point.
     - Valid     -> keep extending this set.
     - Not valid -> abandon this branch. Removing more corridors never makes
                    a trip shorter (monotonicity, Lemma 1), so no superset
                    can become valid again.
4. Bound: if removing every remaining corridor still cannot beat the best
   set found so far, skip the branch.
5. Answer: R = M minus the largest valid removal set.

EXAMPLE (handout maze, 3 x 3, 9 corridors)
   remove {(0,0)-(1,0)}  -> invalid, (0,0) is cut off  -> prune
   remove {(1,0)-(1,1)}  -> valid  -> try adding a 2nd corridor
                            -> every pair is invalid   -> prune
   Best: 1 corridor removed, so R has 8 corridors.

DEPENDENCIES
maze_tools.py
   read_maze            read a maze file   -> (n, m, verts, edges)
   all_pairs_bfs        shortest distances in M
   is_valid_refinement  test the +2 condition for a candidate R
   edge_str             format a corridor as "(r,c)-(r,c)"

Imported by: run_tests.py, experiments.py

RETURNS
solve_baseline(verts, edges) -> (kept_edges, checks)
   kept_edges : list of corridors in an optimal R
   checks     : number of validity checks performed (for comparison with
                fasterAlgo.py in the experiments)

COMPLEXITY
Time  : O(2^|E| * N * |E|)  - up to 2^|E| sets, each checked by N BFS runs.
Space : O(N^2)              - the table of distances in M.

USAGE
   python baseline.py <maze-file> [--quiet]

   --quiet   do not print the list of deleted corridors

Example:
   python baseline.py examples/prof_example.txt
"""

import sys
import time

from maze_tools import read_maze, all_pairs_bfs, is_valid_refinement, edge_str


# Solver

def solve_baseline(verts, edges):
    """
    Find an optimal refined maze R by backtracking over sets of removed corridors.

    Parameters
    verts : list of int
        Points of the maze M (point id = row * m + col).
    edges : list of (int, int)
        Corridors of M, each stored as (smaller id, larger id).

    Returns
    kept_edges : list of (int, int)
        Corridors of an optimal R (minimum number of edges).
    checks : int
        Number of calls to is_valid_refinement.
    """
    # Distances in the original maze M; computed once and reused for every check.
    dist_M = all_pairs_bfs(verts, edges)

    # Fixed order of corridors: E[0], E[1], ..., E[|E|-1].
    E = list(edges)

    # Mutable holders so the nested search() can update them.
    best = [frozenset()]    # largest valid removal set found so far
    checks = [0]            # number of validity checks performed

    def search(start, removed):
        """
        Extend the valid removal set 'removed' with corridors E[start:].

        Invariant: 'removed' is valid on entry. Corridors are added only in
        increasing index order, so every subset of E is visited at most once.
        """
        # Record a new best solution.
        if len(removed) > len(best[0]):
            best[0] = frozenset(removed)

        # Bound: even removing every remaining corridor cannot beat the best.
        if len(removed) + (len(E) - start) <= len(best[0]):
            return

        for j in range(start, len(E)):
            # Try removing corridor E[j] as well.
            removed.add(E[j])
            checks[0] += 1

            kept = [e for e in E if e not in removed]
            if is_valid_refinement(verts, kept, dist_M):
                # Still valid: try removing more corridors.
                search(j + 1, removed)
            # Invalid: prune. By monotonicity, no superset can be valid.

            # Undo, then try the next corridor in its place.
            removed.discard(E[j])

    search(0, set())

    kept_edges = [e for e in E if e not in best[0]]
    return kept_edges, checks[0]


# Command-line entry point

def main():
    """Read a maze file, run the baseline solver, and print the result."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    n, m, verts, edges = read_maze(sys.argv[1])

    t0 = time.perf_counter()
    kept, checks = solve_baseline(verts, edges)
    elapsed = time.perf_counter() - t0

    print(f"maze {n}x{m}: |V|={len(verts)} |E(M)|={len(edges)}")
    print(f"refined maze R: {len(kept)} edges  (deleted {len(edges) - len(kept)})")
    print(f"validity checks: {checks}   time: {elapsed:.3f} s")

    if "--quiet" not in sys.argv:
        kept_set = set(kept)
        removed = [edge_str(e, m) for e in edges if e not in kept_set]
        print("deleted edges:", ", ".join(removed) or "none")


if __name__ == "__main__":
    main()
