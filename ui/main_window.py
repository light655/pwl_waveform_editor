from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QAction
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piece Wise Linear Waveform Editor")

        # Application layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Plotting area
        self.plot_widget = pg.PlotWidget()
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.plot_item.setXRange(-0.05, 1.05, padding=0)
        self.plot_item.setYRange(-1.2, 1.2, padding=0)
        layout.addWidget(self.plot_widget)

        # Menu bar
        self.menu_bar = self.menuBar()

        # File menu
        self.file_menu = self.menu_bar.addMenu("File")
        # Import (TODO)
        # Export
        self.export_action = QAction("Export", self, shortcut="Ctrl+E", statusTip="Export waveform")
        self.export_action.triggered.connect(self.export_waveform)
        self.file_menu.addAction(self.export_action)

        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        # Add points (TODO)
        self.add_point_action = QAction("Add Point", self, shortcut="Ctrl+A", statusTip="Add a new point")
        self.add_point_action.triggered.connect(self.add_point)
        self.edit_menu.addAction(self.add_point_action)
        # Remove points (TODO)
        # Undo (TODO)
        # Redo (TODO)

        self.redraw(0, 0.0, 0.0)  # Initial redraw with default values

    def redraw(self, index, x, y):
        """Redraw the waveform based on updated control points."""
        # Placeholder for actual redraw logic
        print(f"Redrawing waveform at index {index} with new position ({x}, {y})")

    def export_waveform(self):
        """Export the piece wise linear waveform."""
        # Placeholder for actual export logic
        print("Exporting waveform")

    def add_point(self):
        """Add a new control point to the waveform."""
        # Placeholder for actual add point logic
        print("Adding a new point")