from PySide6.QtCore import Signal
import pyqtgraph as pg

class DraggableNode(pg.ScatterPlotItem):
    """A scatter plot item with click-and-drag capability."""
    positionChanged = Signal(int, float, float)  # index, new_x, new_y
    nodeSelected = Signal(int)                   # index

    def __init__(self, parent_canvas, node_idx=0):
        super().__init__(size=14, pen=pg.mkPen(None), brush=pg.mkBrush(255, 80, 80, 230), hoverable=True, selectable=True)
        self.canvas = parent_canvas
        self.node_idx = node_idx
        self.dragging = False
        self.setZValue(100)  # Ensure nodes sit above the curve line

    def mouseClickEvent(self, event):
        if event.button() == pg.QtCore.Qt.LeftButton:
            pts = self.pointsAt(event.pos())
            if len(pts) > 0:
                self.nodeSelected.emit(self.node_idx)
                event.accept()
                return
        event.ignore()

    def mouseDragEvent(self, event):
        if event.button() != pg.QtCore.Qt.LeftButton:
            event.ignore()
            return

        # On drag start: check if mouse is on this node's point
        if event.isStart():
            pts = self.pointsAt(event.buttonDownPos())
            if len(pts) > 0:
                self.dragging = True
                self.nodeSelected.emit(self.node_idx)
                event.accept()
            else:
                event.ignore()
                return

        # While dragging: update position
        if self.dragging:
            pos = self.canvas.plot_item.vb.mapSceneToView(event.scenePos())
            self.positionChanged.emit(self.node_idx, pos.x(), pos.y())
            event.accept()

            if event.isFinish():
                self.dragging = False