"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : fasterAlgo.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 12, 2026

PURPOSE
Faster exact algorithm. It returns the same optimal answer as baseline.py,
but it does far fewer validity checks.

Given a maze M (a connected subgraph of an n x m grid), find a refined maze
R, a subgraph of M with the fewest corridors (edges), such that

       d_R(u, v) <= d_M(u, v) + 2        for every pair of points u, v.

METHOD
It keeps the baseline's backtracking (try corridors in a fixed order, check
with BFS, go deeper only while valid) and adds six ideas from the report:

(0) Special cases, answered directly with no search:
      - a tree (no loops)        -> nothing can be removed, R = M
      - a single cycle           -> remove one corridor only if its length is 4
      - a complete grid with at most 3 rows or 3 columns
                                 -> the "comb" is optimal (Theorem 3)
(1) Square candidates (Lemma 3): only a corridor that lies on a unit square
    can ever be removed, so only those are tried.
(2) Square-rule filter: before running BFS, reject a removal in O(1) if it
    breaks the square rule for the new corridor or for any corridor
    already removed.
(3) Loop cap and early stop (Lemma 4): at most c(M) = |E| - N + 1 removals.
    Reaching c(M) means R is a spanning tree, which is optimal, so stop.
(4) Greedy seed: a quick greedy pass gives a good first answer, so the
    bound prunes from the start.
(5) Square-packing bound (Lemma 5): every removed corridor needs its own
    intact square, so a branch can add at most (number of still-free
    squares) more removals.

EXAMPLE (handout maze, 3 x 3, 9 corridors, 1 loop)
   Candidates: only the 4 corridors of the single unit square.
   Greedy removes (1,0)-(1,1) after 1 BFS check.
   Loop cap c(M) = 1 is reached -> stop. R has 8 corridors.
   Baseline needs 21 checks for the same answer; this needs 1.

DEPENDENCIES
maze_tools.py
   read_maze            read a maze file   -> (n, m, verts, edges)
   all_pairs_bfs        shortest distances in M
   is_valid_refinement  test the +2 condition for a candidate R
   squares_of_edges     the unit squares through each corridor
   edge_str             format a corridor as "(r,c)-(r,c)"

Imported by: run_tests.py, grid_table.py, experiments.py

RETURNS
solve_fast(verts, edges, m, n=None, packing=True) -> (kept_edges, checks)
   kept_edges : list of corridors in an optimal R
   checks     : number of full BFS validity checks performed
   packing    : False switches off idea (5); the answer stays optimal.
                Used only by experiments.py to measure what idea (5) adds.

COMPLEXITY
Time  : O( sum_{i <= q} C(s, i) * N * |E| ), where s = number of square
        corridors and q = min(c(M), number of unit squares) (Theorem 2).
        Still exponential in the worst case, but s <= |E| and q <= c(M).
Space : O(N^2) for the table of distances in M.

USAGE
   python fasterAlgo.py <maze-file> [--quiet]

   --quiet   do not print the list of deleted corridors

Example:
   python fasterAlgo.py examples/prof_example.txt
"""

import sys
import time

from maze_tools import (read_maze, all_pairs_bfs, is_valid_refinement,
                        squares_of_edges, edge_str)


# Special cases (idea 0)

def comb(n, m):
    """
    Build the comb for a complete n x m grid with at most 3 rows or 3 columns.

    The comb is one full middle row (the "spine") plus every vertical
    corridor. Theorem 3 shows it satisfies the +2 rule, and it is a
    spanning tree, so it is optimal. For a tall, thin grid (m <= 3) the
    same shape is turned 90 degrees.

    Parameters
    ----------
    n, m : int
        Number of rows and columns.

    Returns
    -------
    list of (int, int)
        Corridors of the comb, sorted.
    """
    if n <= 3:
        s = (n - 1) // 2                                         # middle row
        T = [(s * m + c, s * m + c + 1) for c in range(m - 1)]   # the spine
        T += [(r * m + c, (r + 1) * m + c)                       # all verticals
              for r in range(n - 1) for c in range(m)]
    else:
        s = (m - 1) // 2                                         # middle column
        T = [(r * m + s, (r + 1) * m + s) for r in range(n - 1)]
        T += [(r * m + c, r * m + c + 1)                         # all horizontals
              for r in range(n) for c in range(m - 1)]
    return sorted(T)


def special_case(verts, edges, n, m):
    """
    Answer the maze directly if it is a special case (idea 0).

    Parameters
    ----------
    verts, edges : the maze M (from read_maze)
    n, m         : grid size

    Returns
    -------
    list of (int, int) or None
        The corridors of an optimal R, or None if M is not a special case.
    """
    nV, nE = len(verts), len(edges)

    # Complete grid with at most 3 rows or columns -> the comb.
    if nV == n * m and nE == n * (m - 1) + m * (n - 1) and min(n, m) <= 3:
        return comb(n, m)

    # Tree (N - 1 corridors, no loops) -> every corridor must stay.
    if nE == nV - 1:
        return list(edges)

    # Single cycle (every point has at most 2 neighbours, N corridors):
    # a 4-cycle can lose one corridor; any longer cycle must stay whole.
    deg = {v: 0 for v in verts}
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    if max(deg.values()) <= 2 and nE == nV:
        return list(edges[1:]) if nV == 4 else list(edges)

    return None


# Solver

def solve_fast(verts, edges, m, n=None, packing=True):
    """
    Find an optimal refined maze R using ideas (0)-(5).

    Parameters
    ----------
    verts : list of int
        Points of the maze M (point id = row * m + col).
    edges : list of (int, int)
        Corridors of M, each stored as (smaller id, larger id).
    m : int
        Number of columns (needed to locate unit squares).
    n : int, optional
        Number of rows; computed from verts if not given.
    packing : bool
        Use the square-packing bound (idea 5). Default True.

    Returns
    -------
    kept_edges : list of (int, int)
        Corridors of an optimal R.
    checks : int
        Number of full BFS validity checks performed.
    """
    if n is None:
        n = max(verts) // m + 1

    # (0) Special cases need no search.
    sc = special_case(verts, edges, n, m)
    if sc is not None:
        return sc, 0

    dist_M = all_pairs_bfs(verts, edges)        # distances in M, computed once
    SQ = squares_of_edges(edges, m)             # unit squares through each corridor
    cand = [e for e in edges if SQ[e]]          # (1) only square corridors
    max_del = len(edges) - (len(verts) - 1)     # (3) loop cap c(M)
    checks = [0]                                # mutable so nested functions can update

    def square_ok(e, removed):
        """True if some unit square through e still has its other 3 sides."""
        return any(all(x not in removed for x in sq) for sq in SQ[e])

    def try_remove(e, removed):
        """
        Add corridor e to 'removed' if the result is still valid.

        Cheap O(1) square checks run first; the full BFS check runs only if
        they pass. Returns True (e stays removed) or False (no change).
        """
        # (2) Square rule for the new corridor.
        if not square_ok(e, removed):
            return False

        removed.add(e)

        # (2) Square rule for every corridor removed earlier.
        if any(not square_ok(f, removed) for f in removed):
            removed.discard(e)
            return False

        # Full BFS check of the +2 condition.
        checks[0] += 1
        if is_valid_refinement(verts, [x for x in edges if x not in removed], dist_M):
            return True

        removed.discard(e)
        return False

    # (5) All unit squares (each as its 4 corridors), and the position of each
    # candidate in the search order.
    squares = sorted({tuple(sorted((e,) + o)) for e in cand for o in SQ[e]})
    pos = {e: j for j, e in enumerate(cand)}

    def upper_bound(start, removed):
        """
        Largest number of removals this branch can still reach.

        Combines the loop cap (Lemma 4) with the square-packing bound
        (Lemma 5). With packing=False only the baseline-style bound is used.
        """
        if not packing:
            return len(removed) + min(len(cand) - start, max_del - len(removed))

        free = 0
        for q in squares:
            # A square with a removed side cannot justify another removal.
            if any(x in removed for x in q):
                continue
            # Count it only if it touches a corridor the search may still try.
            if any(x in pos and pos[x] >= start and x not in removed for x in q):
                free += 1

        return len(removed) + min(free, len(cand) - start, max_del - len(removed))

    # (4) Greedy seed: remove candidates in order whenever still valid.
    greedy = set()
    for e in cand:
        if len(greedy) < max_del:
            try_remove(e, greedy)
    best = [frozenset(greedy)]

    def search(start, removed):
        """
        Backtracking as in the baseline, with the stronger bound and early stop.

        Returns True once a spanning tree is reached (optimal, stop everything).
        """
        # Record a new best solution.
        if len(removed) > len(best[0]):
            best[0] = frozenset(removed)

        # (3) Best is a spanning tree -> optimal, stop the whole search.
        if len(best[0]) == max_del:
            return True

        # (3) + (5) Prune: loop cap reached, or this branch cannot beat the best.
        if len(removed) >= max_del or upper_bound(start, removed) <= len(best[0]):
            return False

        for j in range(start, len(cand)):
            if try_remove(cand[j], removed):
                if search(j + 1, removed):
                    return True
                removed.discard(cand[j])        # undo, then try the next one
        return False

    # (5) Search only if the greedy answer might not be optimal.
    if len(best[0]) < upper_bound(0, set()):
        search(0, set())

    kept_edges = [e for e in edges if e not in best[0]]
    return kept_edges, checks[0]


# Command-line entry point

def main():
    """Read a maze file, run the faster solver, and print the result."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    n, m, verts, edges = read_maze(sys.argv[1])

    t0 = time.perf_counter()
    kept, checks = solve_fast(verts, edges, m, n)
    elapsed = time.perf_counter() - t0

    loops = len(edges) - len(verts) + 1
    print(f"maze {n}x{m}: |V|={len(verts)} |E(M)|={len(edges)} loops={loops}")
    print(f"refined maze R: {len(kept)} edges  (deleted {len(edges) - len(kept)})")
    print(f"validity checks: {checks}   time: {elapsed:.3f} s")

    if "--quiet" not in sys.argv:
        kept_set = set(kept)
        removed = [edge_str(e, m) for e in edges if e not in kept_set]
        print("deleted edges:", ", ".join(removed) or "none")


if __name__ == "__main__":
    main()
