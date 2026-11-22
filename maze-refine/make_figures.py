"""
CMPT 360 - Algorithm Design Module
Option 1: Refining a Maze
File    : make_figures.py
Author  : Md Shahed
NSID    : lsx341
Date    : Nov 16, 2026

PURPOSE
Draw Figures 6 and 7 of the report from the experiment results.

   Figure 6 (figures/fig6_size.png):  running time vs maze size       (Experiment A)
   Figure 7 (figures/fig7_loops.png): running time vs number of loops (Experiment B)

In both figures: dots = single runs, x = run stopped at the time limit,
lines = median per x value. The time axis is logarithmic.

DEPENDENCIES
matplotlib (pip install matplotlib)
results/exp_size.csv and results/exp_loops.csv, written by experiments.py.

USAGE
   pip install matplotlib      (once)
   python make_figures.py      (after python experiments.py)
"""

import csv
import statistics

import matplotlib
matplotlib.use("Agg")                     # draw to files only, no window
import matplotlib.pyplot as plt


# Colours and plot style

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

# (algorithm name in the CSV, colour, legend label)
SERIES = (("baseline", "#eb6834", "baseline"),
          ("fasterAlgo-noPack", "#1baf7a", "fasterAlgo without (5)"),
          ("fasterAlgo", "#2a78d6", "fasterAlgo"))

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


# Helpers

def load(path):
    """
    Read a results CSV file.

    Parameters
    ----------
    path : str
        Path of the CSV file.

    Returns
    -------
    list of dict
        One dict per row; every value is a string.
    """
    with open(path) as f:
        return list(csv.DictReader(f))


def style(ax, xlabel, limit):
    """
    Apply the shared figure style: time-limit line, log scale, labels, legend.

    Parameters
    ----------
    ax : matplotlib Axes
        The axes to style.
    xlabel : str
        Label of the x axis.
    limit : float
        Time limit in seconds, drawn as a dotted line.
    """
    ax.axhline(limit, color=INK2, lw=0.8, ls=":")
    ax.text(ax.get_xlim()[0], limit * 1.2, f"{limit:g} s time limit", fontsize=7, color=INK2)
    ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("time (s), log scale")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=6.5, loc="lower left", bbox_to_anchor=(0, 1.02),
              ncol=3, handlelength=1.5, columnspacing=1.0, borderaxespad=0)


# Plotting

def plot(rows, key, xlabel, out):
    """
    Draw one figure: every run as a dot (or x), and the median as a line.

    Parameters
    ----------
    rows : list of dict
        Rows from load().
    key : function
        Maps a row to its x value (e.g. number of vertices).
    xlabel : str
        Label of the x axis.
    out : str
        Path of the PNG file to write.
    """
    # Time limit = the time recorded for timed-out runs (30 s if none timed out).
    limit = max(float(r["seconds"]) for r in rows if r["solved"] == "0") if any(
        r["solved"] == "0" for r in rows) else 30

    fig, ax = plt.subplots(figsize=(3.2, 2.1))
    for algo, col, name in SERIES:
        # Group this algorithm's runs by x value.
        R = [r for r in rows if r["algo"] == algo]
        groups = {}
        for r in R:
            groups.setdefault(key(r), []).append(r)
        xs = sorted(groups)

        # Single runs; times are floored at 1e-4 s so they fit on a log scale.
        for x in xs:
            for r in groups[x]:
                ax.scatter(x, max(float(r["seconds"]), 1e-4), s=9, color=col, alpha=0.35,
                           marker="o" if r["solved"] == "1" else "x", linewidths=1, zorder=2)

        # Median line.
        med = [statistics.median(max(float(r["seconds"]), 1e-4) for r in groups[x]) for x in xs]
        ax.plot(xs, med, color=col, lw=2, zorder=3, label=name)

    style(ax, xlabel, limit)
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out)


# Command-line entry point

def main():
    """Draw Figures 6 and 7."""
    A = load("results/exp_size.csv")
    plot(A, lambda r: int(r["V"]), "number of vertices |V|  (loop probability 0.3)",
         "figures/fig6_size.png")
    B = load("results/exp_loops.csv")
    plot(B, lambda r: int(r["loops"]), "number of loops c  (5 x 5 mazes)",
         "figures/fig7_loops.png")


if __name__ == "__main__":
    main()
