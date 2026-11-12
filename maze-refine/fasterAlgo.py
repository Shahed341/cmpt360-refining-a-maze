"""
fasterAlgo.py - faster exact algorithm for "Refining a Maze" (CMPT 360, Option 1).

It gives the same (optimal) answer as baseline.py, with far fewer checks.
It keeps the baseline's search (try corridors in order, check with BFS, go deeper only
if valid) and adds five ideas from Section 2 of the report:

 (0) Special cases, answered directly with no search:
       - no loops (a tree): nothing can be deleted, R = M
       - a single cycle: one edge can go only if the cycle has length 4
       - a complete grid with at most 3 rows (or 3 columns): the "comb" is optimal
 (1) Square candidates (Lemma 3): only corridors that lie on a unit square can ever
     be deleted, so the search only tries those.
 (2) Quick square check before BFS: a deletion is rejected in O(1) if it breaks the
     square rule for the new corridor or for any corridor already deleted.
 (3) Loop cap and early stop (Lemma 4): at most c = |E| - |V| + 1 deletions; reaching
     c means R is a spanning tree, which is optimal, so stop.
 (4) Greedy seed: a quick greedy pass gives a good first answer for the bound.
 (5) Square-packing bound (Lemma 5): each deleted corridor needs its own square, so a
     branch can add at most (number of still-free squares) more deletions.

Usage:  python fasterAlgo.py <maze-file> [--quiet]
"""
import sys
import time
from maze_tools import (read_maze, all_pairs_bfs, is_valid_refinement,
                        squares_of_edges, edge_str)


def comb(n, m):
    """The comb for a complete n x m grid with at most 3 rows (or 3 columns).

    One full middle row (the "spine") plus every vertical corridor. Theorem 3 in the
    report proves it satisfies the +2 rule, and it is a spanning tree, so it is optimal.
    If the grid is tall and thin (m <= 3), the same idea is turned 90 degrees.
    """
    if n <= 3:
        s = (n - 1) // 2                                          # middle row
        T = [(s * m + c, s * m + c + 1) for c in range(m - 1)]    # the spine
        T += [(r * m + c, (r + 1) * m + c) for r in range(n - 1) for c in range(m)]
    else:
        s = (m - 1) // 2                                          # middle column
        T = [(r * m + s, (r + 1) * m + s) for r in range(n - 1)]
        T += [(r * m + c, r * m + c + 1) for r in range(n) for c in range(m - 1)]
    return sorted(T)


def special_case(verts, edges, n, m):
    """Idea (0): return the answer directly if M is a special case, otherwise None."""
    nV, nE = len(verts), len(edges)
    # complete grid with at most 3 rows or columns -> the comb
    if nV == n * m and nE == n * (m - 1) + m * (n - 1) and min(n, m) <= 3:
        return comb(n, m)
    # a tree (N - 1 corridors, no loops) -> every corridor must stay
    if nE == nV - 1:
        return list(edges)
    # a single cycle (every point has 2 neighbours) -> length 4: drop one edge, else keep all
    deg = {v: 0 for v in verts}
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    if max(deg.values()) <= 2 and nE == nV:
        return list(edges[1:]) if nV == 4 else list(edges)
    return None


def solve_fast(verts, edges, m, n=None):
    """Find the smallest valid refined maze R, using ideas (0)-(5).

    Returns (kept_edges, checks), where checks = number of full BFS checks made.
    """
    if n is None:
        n = max(verts) // m + 1
    sc = special_case(verts, edges, n, m)                 # (0)
    if sc is not None:
        return sc, 0

    dist_M = all_pairs_bfs(verts, edges)                  # distances in M, once
    SQ = squares_of_edges(edges, m)                       # squares through each corridor
    cand = [e for e in edges if SQ[e]]                    # (1) only square corridors
    max_del = len(edges) - (len(verts) - 1)               # (3) loop cap c(M)
    checks = [0]

    def square_ok(e, removed):
        """Square rule: some square through e still has its other 3 sides."""
        return any(all(x not in removed for x in sq) for sq in SQ[e])

    def try_remove(e, removed):
        """Add e to 'removed' if the result is still valid; return True/False."""
        if not square_ok(e, removed):                     # (2) quick check for e
            return False
        removed.add(e)
        if any(not square_ok(f, removed) for f in removed):   # (2) earlier deletions
            removed.discard(e)
            return False
        checks[0] += 1                                    # only now the full BFS check
        if is_valid_refinement(verts, [x for x in edges if x not in removed], dist_M):
            return True
        removed.discard(e)
        return False

    # (5) all unit squares (as 4 corridors), and each candidate's position in the order
    squares = sorted({tuple(sorted((e,) + o)) for e in cand for o in SQ[e]})
    pos = {e: j for j, e in enumerate(cand)}

    def upper_bound(start, removed):
        """Most deletions this branch can still reach (Lemma 5 + Lemma 4)."""
        free = 0
        for q in squares:
            if any(x in removed for x in q):
                continue              # a square with a deleted side can't justify a new one
            if any(x in pos and pos[x] >= start and x not in removed for x in q):
                free += 1             # still free and touches a corridor we may still try
        return len(removed) + min(free, len(cand) - start, max_del - len(removed))

    # (4) greedy first answer: delete candidates in order whenever still valid
    greedy = set()
    for e in cand:
        if len(greedy) < max_del:
            try_remove(e, greedy)
    best = [frozenset(greedy)]

    def search(start, removed):
        """Same backtracking as the baseline, with the stronger bound and early stop."""
        if len(removed) > len(best[0]):
            best[0] = frozenset(removed)
        if len(best[0]) == max_del:                       # (3) spanning tree -> optimal
            return True
        if len(removed) >= max_del or upper_bound(start, removed) <= len(best[0]):
            return False                                  # (5) this branch can't win
        for j in range(start, len(cand)):
            if try_remove(cand[j], removed):
                if search(j + 1, removed):
                    return True
                removed.discard(cand[j])                  # undo and try the next one
        return False

    if len(best[0]) < upper_bound(0, set()):              # (5) greedy may already be optimal
        search(0, set())
    kept = [e for e in edges if e not in best[0]]
    return kept, checks[0]


def main():
    """Command line: read the maze file, solve it, print the result."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    n, m, verts, edges = read_maze(sys.argv[1])
    t0 = time.perf_counter()
    kept, checks = solve_fast(verts, edges, m, n)
    t = time.perf_counter() - t0
    loops = len(edges) - len(verts) + 1
    print(f"maze {n}x{m}: |V|={len(verts)} |E(M)|={len(edges)} loops={loops}")
    print(f"refined maze R: {len(kept)} edges  (deleted {len(edges) - len(kept)})")
    print(f"validity checks: {checks}   time: {t:.3f} s")
    if "--quiet" not in sys.argv:
        removed = [edge_str(e, m) for e in edges if e not in set(kept)]
        print("deleted edges:", ", ".join(removed) or "none")


if __name__ == "__main__":
    main()
