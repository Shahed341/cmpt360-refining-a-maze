# Refining a Maze
CMPT 360 – Algorithm Design Module, Option 1
Md Shahed (lsx341)

## Main files
- `baseline.py` – exact baseline (backtracking with BFS checks)
- `fasterAlgo.py` – faster exact algorithm (same answer, far fewer checks)

## Requirements
Python 3.8 or newer. `make_figures.py` also needs `pip install matplotlib`.

## How to run
Run every command from inside this folder.

python baseline.py examples/prof_example.txt           # handout maze -> R has 8 edges
python fasterAlgo.py examples/prof_example.txt         # same answer

Add `--quiet` to hide the list of deleted edges.


### To make your own maze:
python generate.py 5 5 0.5 7 examples/random_5x5.txt   # rows cols loop_prob seed file
python generate.py full 3 6 examples/full_3x6.txt      # complete grid

## Reproducing the report
python run_tests.py       # all tests (about 10 s)
python grid_table.py      # Table 1
python experiments.py     # Section 5 experiments (about 30-45 min, overwrites results/)
python summarize.py       # Table 2
python make_figures.py    # Figures 6 and 7

## Maze file format
- # comment
- n m            rows, columns
- k              number of corridors
- r1 c1 r2 c2    one line per corridor