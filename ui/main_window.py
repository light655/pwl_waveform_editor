from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QAction
import pyqtgraph as pg

from core.pwl_model import sciparse, sciprint, PWLWaveform
from ui.draggable_nodes import DraggableNode

class MainWindow(QMainWindow):
    def __init__(self, verbose=False):
        super().__init__()
        self.setWindowTitle("Piece Wise Linear Waveform Editor")
        self.verbose = verbose

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

        # options and status bar
        bottom_layout = QHBoxLayout()

        # Checkbox for toggling unit multipliers
        self.unit_checkbox = QCheckBox("Use Unit Multipliers")
        self.unit_checkbox.setCheckable(True)
        self.unit_checkbox.setChecked(True)
        self.unit_checkbox.stateChanged.connect(self.toggle_unit_multipliers)
        bottom_layout.addWidget(self.unit_checkbox)
        bottom_layout.addStretch()

        # Coordinate display
        self.coord_label = QLabel("Selected Point:")
        self.coord_box = QLineEdit()
        self.coord_box.setReadOnly(True)
        self.coord_box.setPlaceholderText("No point selected")
        self.coord_box.setFixedWidth(200)
        bottom_layout.addWidget(self.coord_label)
        bottom_layout.addWidget(self.coord_box)
        layout.addLayout(bottom_layout)

        # Menu bar
        self.menu_bar = self.menuBar()

        # File menu
        self.file_menu = self.menu_bar.addMenu("File")
        # Import (TODO)
        self.import_action = QAction("Import", self, shortcut="Ctrl+I", statusTip="Import waveform")
        self.import_action.triggered.connect(self.import_waveform)
        self.file_menu.addAction(self.import_action)
        # Export
        self.export_action = QAction("Export", self, shortcut="Ctrl+E", statusTip="Export waveform")
        self.export_action.triggered.connect(self.export_waveform)
        self.file_menu.addAction(self.export_action)

        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        # Add point
        self.add_point_action = QAction("Add Point", self, shortcut="A", statusTip="Add a new point")
        self.add_point_action.triggered.connect(self.add_point)
        self.edit_menu.addAction(self.add_point_action)
        # Remove point
        self.remove_point_action = QAction("Remove Point", self, shortcut="D", statusTip="Remove selected point")
        self.remove_point_action.triggered.connect(self.remove_selected_point)
        self.edit_menu.addAction(self.remove_point_action)
        # Move point
        self.move_point_action = QAction("Move Point", self, shortcut="M", statusTip="Move selected point")
        self.move_point_action.triggered.connect(self.move_selected_point)
        self.edit_menu.addAction(self.move_point_action)
        # Undo (TODO)
        # Redo (TODO)

        self.points = []
        self.lines = []
        self.selected_index = None
        self.redraw_all()

    def select_point(self, index):
        """Select a point by index and display its coordinates."""
        if 0 <= index < len(self.waveform.node_x):
            self.selected_index = index
            x = self.waveform.node_x[index]
            y = self.waveform.node_y[index]
            self.print_coordinates(x, y)
            self.update_point_styles()

    def update_point_styles(self):
        """Visually highlight the selected point."""
        for i, node in enumerate(self.points):
            if i == self.selected_index:
                node.setPen(pg.mkPen('k', width=2))
                node.setBrush(pg.mkBrush(255, 200, 0, 255))
            else:
                node.setPen(pg.mkPen(None))
                node.setBrush(pg.mkBrush(255, 80, 80, 230))

    def toggle_unit_multipliers(self):
        """Toggle the use of unit multipliers for displaying coordinates."""
        self.waveform.use_unit_multipliers = self.unit_checkbox.isChecked()

        if self.selected_index is not None and 0 <= self.selected_index < len(self.waveform.node_x):
            x = self.waveform.node_x[self.selected_index]
            y = self.waveform.node_y[self.selected_index]
            self.print_coordinates(x, y)

    def print_coordinates(self, x, y):
        """Print the coordinates of a point, using unit multipliers if enabled."""
        if self.waveform.use_unit_multipliers:
            self.coord_box.setText(f"X: {sciprint(x)}, Y: {sciprint(y)}")
        else:
            self.coord_box.setText(f"X: {x:.3g}, Y: {y:.3g}")

    def redraw_index(self, index, x, y):
        """Redraw the waveform based on updated control points."""

        if self.verbose:
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

        # Update coordinates in textbox if this is the selected point
        if index == self.selected_index:
            self.print_coordinates(x, y)

    def redraw_all(self):
        """Redraw the entire waveform based on all control points."""
        self.plot_widget.clear()
        self.points = []
        self.lines = []
        for idx, (x, y) in enumerate(zip(self.waveform.node_x, self.waveform.node_y)):
            node = DraggableNode(self, node_idx=idx)
            node.setData([x], [y])
            node.positionChanged.connect(self.redraw_index)
            node.nodeSelected.connect(self.select_point)
            self.points.append(node)
            self.plot_widget.addItem(node)

        if len(self.waveform.node_x) > 1:
            for i in range(len(self.waveform.node_x) - 1):
                x0, y0 = self.waveform.node_x[i], self.waveform.node_y[i]
                x1, y1 = self.waveform.node_x[i + 1], self.waveform.node_y[i + 1]
                line = pg.PlotCurveItem(x=[x0, x1], y=[y0, y1], pen=pg.mkPen('#00B4D8', width=2.5))
                self.plot_widget.addItem(line)
                self.lines.append(line)

        # Restore or initialize selection
        if len(self.waveform.node_x) > 0:
            if self.selected_index is None or self.selected_index >= len(self.waveform.node_x):
                self.select_point(0)
            else:
                self.select_point(self.selected_index)
        else:
            self.selected_index = None
            self.coord_box.clear()

    def import_waveform(self):
        """Import a piece wise linear waveform from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Waveform",
            "",
            "CSV Files (*.csv);;PWL Files (*.pwl);;Text Files (*.txt);;All Files (*)",
        )
        if not file_path:
            return

        try:
            self.waveform.import_waveform(file_path)
            self.selected_index = 0 if self.waveform.node_x else None
            self.redraw_all()
            if self.verbose:
                print(f"Imported waveform from {file_path}")

        except Exception as e:
            print(f"Failed to import waveform: {e}")

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

        self.waveform.export_waveform(file_path)

    def add_point(self):
        """Add a new point to the waveform."""
        dialog = AddPointDialog(self)
        if dialog.exec() == QDialog.Accepted:
            x, y = dialog.get_coordinates()
            self.waveform.add_point(x, y)
            try:
                self.selected_index = self.waveform.node_x.index(x)
            except ValueError:
                pass
            self.redraw_all()

            if self.verbose:
                print(f"Adding point at ({sciprint(x)}, {sciprint(y)})")

    def remove_selected_point(self):
        """Remove the currently selected point from the waveform."""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.waveform.node_x):
            removed_x = self.waveform.node_x[self.selected_index]
            removed_y = self.waveform.node_y[self.selected_index]
            del self.waveform.node_x[self.selected_index]
            del self.waveform.node_y[self.selected_index]
            if self.verbose:
                print(f"Removed point at ({sciprint(removed_x)}, {sciprint(removed_y)})")
            # Adjust selected index
            if self.selected_index >= len(self.waveform.node_x):
                self.selected_index = len(self.waveform.node_x) - 1
            self.redraw_all()
            
    def move_selected_point(self):
        """Move the currently selected point in the waveform."""
        if self.selected_index is None or not 0 <= self.selected_index < len(self.waveform.node_x):
            return

        dialog = MovePointDialog(self)
        if dialog.exec() == QDialog.Accepted:
            x, y = dialog.get_coordinates()
            # Remove the old point
            del self.waveform.node_x[self.selected_index]
            del self.waveform.node_y[self.selected_index]
            # Add the new point
            self.waveform.add_point(x, y)
            try:
                self.selected_index = self.waveform.node_x.index(x)
            except ValueError:
                pass
            self.redraw_all()
            if self.verbose:
                print(f"Moving point to ({sciprint(x)}, {sciprint(y)})")

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


class MovePointDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Move Point")
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
        self.add_button = QPushButton("Move Point")
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