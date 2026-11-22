"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : generate.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 16, 2026

PURPOSE
Write maze files for testing: either a random connected maze or a complete
grid, in the format read_maze reads.

METHOD
A random maze is a random spanning tree of the grid (so it is connected)
plus every other grid corridor with probability loop_prob. A bigger
loop_prob gives more loops.

DEPENDENCIES
maze_tools.py
   random_maze   a random connected maze
   full_grid     the complete n x m grid
   write_maze    save a maze to a file

USAGE
   python generate.py <rows> <cols> <loop_prob> <seed> <out-file>   random maze
   python generate.py full <rows> <cols> <out-file>                  complete grid

Examples:
   python generate.py 5 5 0.5 7 examples/random_5x5.txt
   python generate.py full 3 12 examples/full_3x12.txt
"""

import sys

from maze_tools import random_maze, full_grid, write_maze


# Command-line entry point

def main():
    """Read the command line and write the requested maze file."""
    a = sys.argv[1:]

    if a and a[0] == "full" and len(a) == 4:
        # Complete grid: full <rows> <cols> <out-file>
        n, m = int(a[1]), int(a[2])
        _, E = full_grid(n, m)
        write_maze(a[3], n, m, E, f"complete {n}x{m} grid")
    elif len(a) == 5:
        # Random maze: <rows> <cols> <loop_prob> <seed> <out-file>
        n, m, p, seed = int(a[0]), int(a[1]), float(a[2]), int(a[3])
        _, E = random_maze(n, m, p, seed)
        write_maze(a[4], n, m, E, f"random maze {n}x{m}, loop_prob={p}, seed={seed}")
    else:
        print(__doc__)
        sys.exit(1)

    print("wrote", a[-1])


if __name__ == "__main__":
    main()
