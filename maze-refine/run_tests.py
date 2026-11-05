"""
run_tests.py - checks that every piece works. We add more checks after each step.

Run it from the maze-refine folder:   python run_tests.py
If a check fails, Python stops with an AssertionError and shows the line that failed.
"""
from maze_tools import read_maze, all_pairs_bfs, is_valid_refinement, edge_str


# Step 3: reading a maze, measuring distances, checking the +2 rule.
# All expected answers come from the handout maze (see the explainer doc).


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
