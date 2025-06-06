import sys
import os
import pytest
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chart_utils import (
    make_bar_chart,
    make_histogram,
    make_bmi_scatter
)

@pytest.fixture
def sample_data():
    return pd.Series([10, 15, 7, 12, 8], index=["A", "B", "C", "D", "E"])

def test_make_bar_chart(sample_data):
    canvas = make_bar_chart(sample_data, "Test Chart", "X-Axis", "Y-Axis")
    assert isinstance(canvas, FigureCanvas)
    assert canvas.minimumHeight() >= 600

def test_make_histogram(sample_data):
    canvas = make_histogram(sample_data, bins=5, title="Histogram", xlabel="Value", ylabel="Count")
    assert isinstance(canvas, FigureCanvas)
    assert canvas.minimumHeight() >= 600

def test_make_bmi_scatter(sample_data):
    canvas = make_bmi_scatter(sample_data, "BMI Scatter", "Index", "BMI")
    assert isinstance(canvas, FigureCanvas)
