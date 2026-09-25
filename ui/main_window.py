from PySide6.QtWidgets import QDialog, QFileDialog, QLineEdit, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QAction
import pyqtgraph as pg

from core.pwl_model import sciparse, sciprint, PWLWaveform
from ui.draggable_nodes import DraggableNode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piece Wise Linear Waveform Editor")

        self.waveform = PWLWaveform()

        # Application layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Plotting area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
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
        self.add_point_action = QAction("Add Point", self, shortcut="A", statusTip="Add a new point")
        self.add_point_action.triggered.connect(self.add_point)
        self.edit_menu.addAction(self.add_point_action)
        # Remove points (TODO)
        # Undo (TODO)
        # Redo (TODO)

        self.points = []
        self.lines = []
        self.redraw_all()

    def redraw_index(self, index, x, y):
        """Redraw the waveform based on updated control points."""

        print(f"Redrawing index {index} to new position ({sciprint(x)}, {sciprint(y)})")

        # limit the x values between the two neighbouring points to maintain order
        if len(self.waveform.node_x) > 1:
            if index == 0:
                x = min(x, self.waveform.node_x[1])
            elif index == len(self.waveform.node_x) - 1:
                x = max(x, self.waveform.node_x[-2])
            else:
                x = max(x, self.waveform.node_x[index - 1])
                x = min(x, self.waveform.node_x[index + 1])

        # update the position of the point
        self.waveform.update_point_position(index, x, y)
        self.points[index].setData([x], [y])

        # Update the lines connecting the points
        if index > 0:
            x0, y0 = self.waveform.node_x[index - 1], self.waveform.node_y[index - 1]
            x1, y1 = self.waveform.node_x[index], self.waveform.node_y[index]
            self.lines[index - 1].setData(x=[x0, x1], y=[y0, y1])
        if index < len(self.waveform.node_x) - 1:
            x0, y0 = self.waveform.node_x[index], self.waveform.node_y[index]
            x1, y1 = self.waveform.node_x[index + 1], self.waveform.node_y[index + 1]
            self.lines[index].setData(x=[x0, x1], y=[y0, y1])

    def redraw_all(self):
        """Redraw the entire waveform based on all control points."""
        self.plot_widget.clear()
        self.points = []
        self.lines = []
        for idx, (x, y) in enumerate(zip(self.waveform.node_x, self.waveform.node_y)):
            node = DraggableNode(self, node_idx=idx)
            node.setData([x], [y])
            node.positionChanged.connect(self.redraw_index)
            self.points.append(node)
            self.plot_widget.addItem(node)

        if len(self.waveform.node_x) > 1:
            for i in range(len(self.waveform.node_x) - 1):
                x0, y0 = self.waveform.node_x[i], self.waveform.node_y[i]
                x1, y1 = self.waveform.node_x[i + 1], self.waveform.node_y[i + 1]
                line = pg.PlotCurveItem(x=[x0, x1], y=[y0, y1], pen=pg.mkPen('#00B4D8', width=2.5))
                self.plot_widget.addItem(line)
                self.lines.append(line)

    def export_waveform(self):
        """Export the piece wise linear waveform."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Waveform",
            "",
            "CSV Files (*.csv);;PWL Files (*.pwl);;Text Files (*.txt);;All Files (*)",
        )
        if not file_path:
            return

        with open(file_path, 'w') as f:
            for x, y in zip(self.waveform.node_x, self.waveform.node_y):
                f.write(f"{sciprint(x)},{sciprint(y)}\n")
        

    def add_point(self):
        """Add a new point to the waveform."""
        dialog = AddPointDialog(self)
        if dialog.exec() == QDialog.Accepted:
            x, y = dialog.get_coordinates()
            self.waveform.add_point(x, y)
            self.redraw_all()
            print(f"Adding point at ({sciprint(x)}, {sciprint(y)})")

class AddPointDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Point")
        layout = QVBoxLayout(self)

        # Input fields for x and y coordinates
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("Enter x coordinate")
        self.x_input.returnPressed.connect(self.on_accept)
        layout.addWidget(self.x_input)

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Enter y coordinate")
        self.y_input.returnPressed.connect(self.on_accept)
        layout.addWidget(self.y_input)

        # Add button
        self.add_button = QPushButton("Add Point")
        self.add_button.clicked.connect(self.on_accept)
        layout.addWidget(self.add_button)

        self.x = None
        self.y = None

    def on_accept(self):
        """Handle validating input and accepting the dialog."""
        try:
            self.x = sciparse(self.x_input.text())
            self.y = sciparse(self.y_input.text())
            self.accept()
        except ValueError:
            print("Invalid input. Please enter numeric values for x and y.")

    def get_coordinates(self):
        """Return the entered (x, y) coordinates."""
        return self.x, self.y