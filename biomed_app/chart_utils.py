# chart_utils.py
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy

# Globální styl přesně jako v aplikaci
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'axes.edgecolor': '#0D1B2A',
    'axes.linewidth': 1,
    'grid.color': '#888888',
    'grid.alpha': 0.3,
    'figure.autolayout': True
})


def make_bar_chart(data, title, xlabel, ylabel,
                   figsize=(8, 5), dpi=100, min_h=600):
    fig = Figure(figsize=figsize, dpi=dpi, facecolor='white')
    ax = fig.add_subplot(111, facecolor='white')

    data.plot(kind="bar", ax=ax, color="#415A77", edgecolor="#0D1B2A")
    ax.set_title(title, color="#0D1B2A")
    ax.set_xlabel(xlabel, color="#0D1B2A", labelpad=16)
    ax.set_ylabel(ylabel, color="#0D1B2A")

    # otočíme x-štítky vodorovně
    ax.tick_params(axis='x', rotation=0)

    ax.spines['left'].set_color("#0D1B2A")
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_color("#0D1B2A")
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    max_h = data.max() or 0
    ax.set_ylim(0, max_h * 1.4)
    for rect in ax.patches:
        h = rect.get_height()
        ax.text(
            rect.get_x()+rect.get_width()/2,
            h + max_h*0.02,
            f"{int(h)}", ha="center", va="bottom",
            color="#0D1B2A"
        )

    ax.grid(axis="y", color="#888888", alpha=0.3)
    fig.tight_layout()

    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.setMinimumHeight(min_h)
    return canvas


def make_histogram(data, bins, title, xlabel, ylabel,
                   figsize=(8, 5), dpi=100, min_h=600):
    fig = Figure(figsize=figsize, dpi=dpi, facecolor='none')
    ax = fig.add_subplot(111, facecolor='none')

    # histogram
    counts, edges, patches = ax.hist(
        data.dropna(), bins=bins,
        color="#415A77",      # barva výplně
        edgecolor="#0D1B2A"    # barva okraje
    )

    ax.set_title(title)
    ax.set_xlabel(xlabel, labelpad=12)
    ax.set_ylabel(ylabel)

    ax.spines['left'].set_linewidth(1.2)
    ax.spines['left'].set_color('#0D1B2A')
    ax.yaxis.set_ticks_position('left')

    # xticky na přesné intervaly
    ax.set_xticks(edges)
    ax.set_xticklabels([f"{int(e)}" for e in edges], rotation=45)

    # zvětšení rozsahu Y o 40 %, aby se nikde nic neodřelo
    max_h = counts.max()
    ax.set_ylim(0, max_h * 1.4)

    # popisky nad sloupci
    for rect, cnt in zip(patches, counts):
        ax.text(
            rect.get_x() + rect.get_width()/2,
            cnt + max_h * 0.02,
            f"{int(cnt)}",
            ha='center', va='bottom'
        )

    ax.grid(axis='y')
    ax.tick_params(axis='x', rotation=0)
    fig.tight_layout()

    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.setMinimumHeight(min_h)
    return canvas


def make_bmi_scatter(data, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.scatter(range(len(data)), data, color='red')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    return FigureCanvas(fig)
