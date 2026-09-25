from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piece Wise Linear Waveform Editor")