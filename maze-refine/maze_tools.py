"""
maze_tools.py - the toolbox for "Refining a Maze" (CMPT 360, Option 1).

Every other file (baseline.py, fasterAlgo.py, the experiments) imports these tools:
    read_maze            read a maze from a text file
    edge_str             print a corridor in a readable way, e.g. (1,0)-(1,1)
    all_pairs_bfs        measure the shortest distance between every pair of points
    is_valid_refinement  check the +2 rule for a smaller maze R

How points are stored:
    A point (row r, column c) gets the number  id = r * m + c,  where m = number of columns.
    Example in a 3 x 3 grid:  (0,0) -> 0,  (1,0) -> 3,  (1,1) -> 4,  (2,2) -> 8.
    A corridor is a pair of point numbers, smaller first:  (1,0)-(1,1)  ->  (3, 4).

Maze file format (lines starting with # are comments and are skipped):
    n m            grid size: n rows, m columns
    k              number of corridors
    r1 c1 r2 c2    one line per corridor, joining (r1,c1) and (r2,c2)
"""
from collections import deque


def read_maze(path):
    """Read a maze file and return (n, m, points, corridors).

    n, m       grid size (rows, columns)
    points     sorted list of point numbers that appear in some corridor
    corridors  sorted list of pairs (a, b) with a < b

    Example: the line "1 0 1 1" becomes the corridor (3, 4) in a 3-column grid.
    It also checks that every corridor joins two neighbouring grid points.
    """
    # 1. Collect every number in the file, skipping comments and blank lines.
    nums = []
    with open(path) as f:
        for line in f:
            line = line.split("#", 1)[0].strip()      # keep only the part before '#'
            if line:
                nums.extend(int(x) for x in line.split())

    # 2. The first three numbers are: rows, columns, number of corridors.
    n, m, k = nums[0], nums[1], nums[2]

    # 3. Each corridor uses the next 4 numbers: r1 c1 r2 c2.
    edges = []
    for i in range(k):
        r1, c1, r2, c2 = nums[3 + 4 * i: 7 + 4 * i]
        # neighbours differ by exactly 1 step up/down or left/right
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            raise ValueError(f"({r1},{c1})-({r2},{c2}) is not a grid edge")
        a, b = r1 * m + c1, r2 * m + c2               # (row, col) -> point number
        edges.append((min(a, b), max(a, b)))          # store smaller number first

    # 4. Remove duplicates, sort, and list the points that are used.
    edges = sorted(set(edges))
    verts = sorted({v for e in edges for v in e})
    return n, m, verts, edges


def edge_str(e, m):
    """Turn a corridor (a, b) back into readable text.

    Example (3 columns): edge_str((3, 4), 3) -> "(1,0)-(1,1)".
    A point number p is row p // m, column p % m.
    """
    a, b = e
    return f"({a // m},{a % m})-({b // m},{b % m})"


def all_pairs_bfs(verts, edges):
    """Shortest distance between every pair of points, by BFS from every point.

    Returns a dictionary of dictionaries:  dist[u][v] = fewest corridors from u to v.
    Example (handout maze): dist[0][8] = 4, the walk (0,0)->(1,0)->(1,1)->(2,1)->(2,2).

    How BFS works: start at s with distance 0, then visit its neighbours (distance 1),
    then their unvisited neighbours (distance 2), and so on, like a ripple in water.
    Time: one BFS is O(V + E), done from all V points -> O(V * (V + E)).
    """
    # Build the neighbour list of every point.
    adj = {v: [] for v in verts}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    dist = {}
    for s in verts:                       # one BFS from every starting point s
        d = {s: 0}                        # distance from s to each point reached so far
        q = deque([s])                    # queue of points waiting to be expanded
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in d:            # first time we reach y = shortest distance
                    d[y] = d[x] + 1
                    q.append(y)
        dist[s] = d
    return dist


def is_valid_refinement(verts, kept_edges, dist_M, slack=2):
    """Check the +2 rule: is R = (verts, kept_edges) an allowed refined maze?

    Returns True only if
      1. R is connected (every point can still reach every other point), and
      2. for every pair u, v:  d_R(u, v) <= d_M(u, v) + slack   (slack = 2).
    dist_M is the distance table of the original maze M, from all_pairs_bfs.

    Example (handout maze): removing (1,0)-(1,1) -> True  (worst trip grows by 2);
                            removing (0,0)-(1,0) -> False ((0,0) is cut off).

    It runs one BFS from every point in R and stops at the first broken rule.
    Time: O(V * (V + E)) in the worst case.
    """
    # Build the neighbour list of R (only the corridors we kept).
    adj = {v: [] for v in verts}
    for a, b in kept_edges:
        adj[a].append(b)
        adj[b].append(a)

    nV = len(verts)
    for s in verts:
        # BFS from s inside R
        d = {s: 0}
        q = deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in d:
                    d[y] = d[x] + 1
                    q.append(y)

        if len(d) < nV:                   # rule 1 broken: some point is unreachable
            return False
        dM = dist_M[s]
        for t, x in d.items():
            if x > dM[t] + slack:         # rule 2 broken: trip s -> t grew by more than 2
                return False
    return True                           # every pair passed both rules
