import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtWidgets import QLabel, QPushButton
from ui_helpers import CollapsibleSection, add_download_button

def test_collapsible_section_initial_state(qtbot):
    section = CollapsibleSection("Test Section")
    qtbot.addWidget(section)

    assert not section.toggle_button.isChecked()
    assert not section.content_area.isVisible()
    assert section.content_area.maximumHeight() == 0

def test_collapsible_section_toggle(qtbot):
    section = CollapsibleSection("Test Section")
    qtbot.addWidget(section)
    section.add_widget(QLabel("Test content"))
    section.show()

    section.toggle_button.click()
    qtbot.wait(50)

    assert section.toggle_button.isChecked()
    assert section.content_area.isVisible()
    assert section.content_area.maximumHeight() > 0

    section.toggle_button.click()
    qtbot.wait(50)

    assert not section.toggle_button.isChecked()
    assert not section.content_area.isVisible()
    assert section.content_area.maximumHeight() == 0


def test_add_widget_to_section(qtbot):
    section = CollapsibleSection("Test Section")
    qtbot.addWidget(section)
    label = QLabel("Sample Widget")
    section.add_widget(label)

    assert section.content_layout.count() == 1

def test_add_download_button(qtbot):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

    fig = Figure()
    canvas = FigureCanvas(fig)
    widget = add_download_button(canvas, "Save it")
    qtbot.addWidget(widget)

    assert widget.layout().count() == 2
    assert isinstance(widget.layout().itemAt(0).widget(), FigureCanvas)
    assert isinstance(widget.layout().itemAt(1).widget(), QPushButton)
