# chart_utils.py

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore

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
                   figsize=(8,5), dpi=100, min_h=600):
    # transparentní pozadí figury i osy
    fig = Figure(figsize=figsize, dpi=dpi, facecolor='none')
    ax  = fig.add_subplot(111, facecolor='none')

    # vykreslení pruhů (výchozí barva)
    data.plot(kind='bar', ax=ax)

    # nadpisy a popisky os
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # zvýrazněná levá osa
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['left'].set_color('#0D1B2A')
    ax.yaxis.set_ticks_position('left')

    # zvětšení rozsahu Y o 10 %, aby štítky nevytékal
    max_h = data.max()
    ax.set_ylim(0, max_h * 1.1)

    # číselné popisky nad každým sloupcem
    for rect in ax.patches:
        h = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width()/2,
            h + max_h * 0.02,
            f"{int(h)}",
            ha='center', va='bottom'
        )

    # lehká mřížka na ose Y
    ax.grid(axis='y')
    fig.tight_layout()

    # převod na Qt Canvas
    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.setMinimumHeight(min_h)
    return canvas

def make_histogram(data, bins, title, xlabel, ylabel,
                   figsize=(8,5), dpi=100, min_h=600):
    fig = Figure(figsize=figsize, dpi=dpi, facecolor='none')
    ax  = fig.add_subplot(111, facecolor='none')

    # histogram
    counts, edges, patches = ax.hist(data.dropna(), bins=bins)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
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
    fig.tight_layout()

    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.setMinimumHeight(min_h)
    return canvas
