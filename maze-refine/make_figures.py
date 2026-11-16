"""
make_figures.py - draws Figures 6 and 7 of the report from the experiment results.

Figure 6 (figures/fig6_size.png):  running time vs maze size     (Experiment A)
Figure 7 (figures/fig7_loops.png): running time vs number of loops (Experiment B)
Dots = single runs, x = run stopped at the time limit, lines = median.

Usage:  pip install matplotlib      (once)
        python make_figures.py      (after python experiments.py)
"""
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SERIES = (("baseline", "#eb6834", "baseline"),
          ("fasterAlgo-noPack", "#1baf7a", "fasterAlgo without (5)"),
          ("fasterAlgo", "#2a78d6", "fasterAlgo"))
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


def load(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def style(ax, xlabel, limit):
    ax.axhline(limit, color=INK2, lw=0.8, ls=":")
    ax.text(ax.get_xlim()[0], limit * 1.2, f"{limit:g} s time limit", fontsize=7, color=INK2)
    ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("time (s), log scale")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=6.5, loc="lower left", bbox_to_anchor=(0, 1.02),
              ncol=3, handlelength=1.5, columnspacing=1.0, borderaxespad=0)


def plot(rows, key, xlabel, out):
    limit = max(float(r["seconds"]) for r in rows if r["solved"] == "0") if any(
        r["solved"] == "0" for r in rows) else 30
    fig, ax = plt.subplots(figsize=(3.2, 2.1))
    for algo, col, name in SERIES:
        R = [r for r in rows if r["algo"] == algo]
        groups = {}
        for r in R:
            groups.setdefault(key(r), []).append(r)
        xs = sorted(groups)
        for x in xs:
            for r in groups[x]:
                ax.scatter(x, max(float(r["seconds"]), 1e-4), s=9, color=col, alpha=0.35,
                           marker="o" if r["solved"] == "1" else "x", linewidths=1, zorder=2)
        med = [statistics.median(max(float(r["seconds"]), 1e-4) for r in groups[x]) for x in xs]
        ax.plot(xs, med, color=col, lw=2, zorder=3, label=name)
    style(ax, xlabel, limit)
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out)


def main():
    A = load("results/exp_size.csv")
    plot(A, lambda r: int(r["V"]), "number of vertices |V|  (loop probability 0.3)",
         "figures/fig6_size.png")
    B = load("results/exp_loops.csv")
    plot(B, lambda r: int(r["loops"]), "number of loops c  (5 x 5 mazes)",
         "figures/fig7_loops.png")


if __name__ == "__main__":
    main()
