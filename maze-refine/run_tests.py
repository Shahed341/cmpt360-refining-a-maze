"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : run_tests.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 5, 2026

PURPOSE
Check that every piece works. Tests were added after each step of the
project, so they are grouped by step:

   Step 3   reading a maze, measuring distances, checking the +2 rule
   Step 4   the brute-force baseline finds the smallest valid R
   Step 5   random mazes and complete grids
   Step 6   fasterAlgo gives exactly the same optimum as the baseline
   Step 8   switching off the packing bound does not change the answer

All expected answers for the handout maze come from the explainer doc.

DEPENDENCIES
maze_tools.py   read_maze, write_maze, all_pairs_bfs, is_valid_refinement,
                edge_str, full_grid, random_maze
baseline.py     solve_baseline
fasterAlgo.py   solve_fast
examples/prof_example.txt (the handout maze)

USAGE
   python run_tests.py      (run from the maze-refine folder)

If a check fails, Python stops with an AssertionError and shows the line
that failed.
"""

from maze_tools import read_maze, all_pairs_bfs, is_valid_refinement, edge_str


# Step 3: reading a maze, measuring distances, checking the +2 rule.

# Test 1: the file is read correctly -> 3 x 3 grid, 9 points, 9 corridors.
n, m, V, E = read_maze("examples/prof_example.txt")
print("grid", n, "x", m, "| points:", len(V), "| corridors:", len(E))
assert (n, m, len(V), len(E)) == (3, 3, 9, 9)

# Test 2: distances are right -> (0,0) to (2,2) takes 4 steps.
# Point numbers: (0,0) = 0 and (2,2) = 2*3 + 2 = 8.
dM = all_pairs_bfs(V, E)
print("distance (0,0) -> (2,2) in M:", dM[0][8])
assert dM[0][8] == 4

# Test 3: keeping every corridor is always allowed (no trip changes).
assert is_valid_refinement(V, E, dM)

# Test 4: removing one side of the loop is allowed, and leaves 8 corridors.
# (1,0) = 3 and (1,1) = 4, so the corridor (1,0)-(1,1) is (3, 4).
e = (3, 4)
R = [x for x in E if x != e]
assert is_valid_refinement(V, R, dM)
print("remove", edge_str(e, m), "-> allowed, R has", len(R), "corridors")

# Test 5: removing a dead end is not allowed, because (0,0) gets cut off.
# (0,0) = 0 and (1,0) = 3, so the corridor (0,0)-(1,0) is (0, 3).
e = (0, 3)
assert not is_valid_refinement(V, [x for x in E if x != e], dM)
print("remove", edge_str(e, m), "-> NOT allowed, (0,0) is cut off")

print("Step 3 tests passed")


# Step 4: the brute-force baseline finds the smallest valid R.

from baseline import solve_baseline

# Test 6: the handout maze -> best R has 8 corridors, and it is valid.
kept, checks = solve_baseline(V, E)
assert len(kept) == 8 and is_valid_refinement(V, kept, dM)
print("baseline, handout maze: R has", len(kept), "corridors after", checks, "checks")

# Test 7: the full 2 x 3 grid (6 points, 7 corridors) -> best R has 5 corridors.
#   (0,0)=0 (0,1)=1 (0,2)=2
#   (1,0)=3 (1,1)=4 (1,2)=5
V2 = [0, 1, 2, 3, 4, 5]
E2 = [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
kept2, _ = solve_baseline(V2, E2)
assert len(kept2) == 5 and is_valid_refinement(V2, kept2, all_pairs_bfs(V2, E2))
print("baseline, full 2 x 3 grid: R has", len(kept2), "corridors")

# Test 8: a maze with no loops (a straight corridor of 4 points) -> nothing can go.
V3 = [0, 1, 2, 3]
E3 = [(0, 1), (1, 2), (2, 3)]
kept3, _ = solve_baseline(V3, E3)
assert kept3 == E3
print("baseline, maze without loops: keeps all", len(kept3), "corridors")

print("Step 4 tests passed")


# Step 5: random mazes and complete grids (used for all later testing).

from maze_tools import full_grid, random_maze, write_maze

# Test 9: the complete 2 x 3 grid has 6 points and 7 corridors (same as Test 7).
Vf, Ef = full_grid(2, 3)
assert len(Vf) == 6 and sorted(Ef) == sorted(E2)

# Test 10: random mazes are connected, use only grid corridors, and the same seed
# gives the same maze. loop_prob 0 gives a tree (no loops), 1 gives the full grid.
for seed in range(20):
    Vr, Er = random_maze(4, 5, 0.4, seed)
    dist = all_pairs_bfs(Vr, Er)
    assert all(len(dist[v]) == len(Vr) for v in Vr)          # every point reaches all
    assert set(Er) <= set(full_grid(4, 5)[1])                 # only real grid corridors
    assert random_maze(4, 5, 0.4, seed) == (Vr, Er)           # repeatable
assert len(random_maze(4, 5, 0.0, 1)[1]) == 20 - 1           # tree: N - 1 corridors
assert random_maze(4, 5, 1.0, 1)[1] == full_grid(4, 5)[1]    # every corridor
print("random mazes: connected, repeatable, tree at p=0, full grid at p=1")

# Test 11: saving a maze and reading it back gives the same maze.
Vr, Er = random_maze(3, 4, 0.5, 7)
write_maze("examples/_test_roundtrip.txt", 3, 4, Er, "test file")
assert read_maze("examples/_test_roundtrip.txt") == (3, 4, Vr, Er)
import os
os.remove("examples/_test_roundtrip.txt")                     # clean up the test file

# Test 12: the baseline gives a valid answer on 10 small random mazes.
for seed in range(10):
    Vr, Er = random_maze(3, 3, 0.5, seed)
    kept, _ = solve_baseline(Vr, Er)
    assert is_valid_refinement(Vr, kept, all_pairs_bfs(Vr, Er))
    assert len(kept) >= len(Vr) - 1                           # R is at least a tree
print("baseline: valid answers on 10 random 3 x 3 mazes")

print("Step 5 tests passed")


# Step 6: fasterAlgo gives exactly the same optimum as the baseline.

from fasterAlgo import solve_fast

# Test 13: the handout maze -> 8 corridors, valid, and no more checks than the baseline.
kf, cf = solve_fast(V, E, m)
kb, cb = solve_baseline(V, E)
assert len(kf) == 8 and is_valid_refinement(V, kf, dM) and cf <= cb
print("fasterAlgo, handout maze: R has", len(kf), "corridors after", cf, "checks (baseline:", cb, ")")

# Test 14: same optimum as the baseline on 40 random mazes, and every answer is valid.
for seed in range(40):
    n_, m_ = [(3, 3), (3, 4), (4, 4), (2, 6)][seed % 4]
    Vr, Er = random_maze(n_, m_, [0.3, 0.6, 1.0][seed % 3], seed)
    kb, _ = solve_baseline(Vr, Er)
    kf, _ = solve_fast(Vr, Er, m_, n_)
    assert len(kf) == len(kb), (n_, m_, seed)
    assert is_valid_refinement(Vr, kf, all_pairs_bfs(Vr, Er))
print("fasterAlgo agrees with the baseline on 40 random mazes")

# Test 15: complete grids with at most 3 rows -> the comb, a spanning tree (Theorem 3).
for n_, m_ in [(2, 5), (3, 3), (3, 6), (6, 2)]:
    Vf, Ef = full_grid(n_, m_)
    kf, _ = solve_fast(Vf, Ef, m_, n_)
    assert len(kf) == n_ * m_ - 1 and is_valid_refinement(Vf, kf, all_pairs_bfs(Vf, Ef))
print("fasterAlgo: thin complete grids give a spanning tree (Theorem 3)")

print("Step 6 tests passed")


# Step 8: switching off the packing bound (used in the experiments) must not
# change the answer, only the speed.

# Test 16: fasterAlgo with and without idea (5) give the same optimum.
for seed in range(20):
    Vr, Er = random_maze(4, 4, [0.3, 0.6][seed % 2], seed)
    a, _ = solve_fast(Vr, Er, 4, 4, packing=True)
    b, _ = solve_fast(Vr, Er, 4, 4, packing=False)
    assert len(a) == len(b)
print("fasterAlgo: same optimum with and without the packing bound")

print("Step 8 tests passed")
