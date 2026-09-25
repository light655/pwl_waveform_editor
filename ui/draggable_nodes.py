from PySide6.QtCore import Signal
import pyqtgraph as pg

class DraggableNode(pg.ScatterPlotItem):
    """A scatter plot item with click-and-drag capability."""
    positionChanged = Signal(int, float, float)  # index, new_x, new_y

    def __init__(self, parent_canvas):
        super().__init__(size=14, pen=pg.mkPen(None), brush=pg.mkBrush(255, 80, 80, 230), hoverable=True)
        self.canvas = parent_canvas
        self.drag_idx = None

    def mousePressEvent(self, event):
        if event.button() == pg.QtCore.Qt.LeftButton:
            pts = self.pointsAt(event.pos())
            if len(pts) > 0:
                self.drag_idx = pts[0].index()
                event.accept()
                return
        event.ignore()

    def mouseDragEvent(self, event):
        if self.drag_idx is not None and event.button() == pg.QtCore.Qt.LeftButton:
            pos = self.canvas.plot_item.vb.mapSceneToView(event.scenePos())
            self.positionChanged.emit(self.drag_idx, pos.x(), pos.y())
            event.accept()
            if event.isFinish():
                self.drag_idx = None
            return
        event.ignore()