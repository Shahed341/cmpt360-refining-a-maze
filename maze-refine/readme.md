# Refining a Maze (CMPT 360, Algorithm Design Module, Option 1)

Given a maze M (a connected subgraph of an n x m grid), find a subgraph R with the
fewest edges such that d_R(u, v) <= d_M(u, v) + 2 for every pair of points u, v.

## Files

| File | What it does |
|---|---|
| `baseline.py` | Exact baseline: backtracking over sets of deleted corridors, BFS check, stop on failure |
| `fasterAlgo.py` | Faster exact algorithm: special cases, square rule, loop cap, greedy seed, square-packing bound |
| `maze_tools.py` | Shared tools: read/write mazes, BFS distances, the +2 check, unit squares, random mazes |
| `generate.py` | Writes a random maze or a complete grid to a file |
| `run_tests.py` | Tests for every step (both algorithms agree, answers are valid) |
| `grid_table.py` | Produces Table 1 (complete grids) |
| `experiments.py` | Runs the timed experiments of Section 5 and writes `results/*.csv` |
| `summarize.py` | Prints Table 2 and the numbers used in Section 5 |
| `make_figures.py` | Draws Figures 6 and 7 from the results |
| `examples/` | Example mazes, including the one from the assignment handout |

## Requirements

Python 3.8 or newer. Only `make_figures.py` needs an extra package: `pip install matplotlib`.

## How to run (inside this folder)

```
python baseline.py examples/prof_example.txt        # handout maze -> 8 edges
python fasterAlgo.py examples/prof_example.txt      # same answer, fewer checks
python generate.py 5 5 0.5 7 examples/random_5x5.txt
python fasterAlgo.py examples/random_5x5.txt
python run_tests.py                                  # all tests, about 5 seconds
python grid_table.py                                 # Table 1 (6x6 takes a few minutes)
python experiments.py                                # Section 5, about 30-45 minutes
python summarize.py                                  # Table 2 and key numbers
python make_figures.py                               # Figures 6 and 7
```

Add `--quiet` to `baseline.py` or `fasterAlgo.py` to hide the list of deleted edges.

## Maze file format

```
# comment lines start with #
n m            grid size (rows, columns)
k              number of corridors
r1 c1 r2 c2    one line per corridor, joining (r1,c1) and (r2,c2)
```
