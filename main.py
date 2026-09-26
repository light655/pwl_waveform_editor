import argparse
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    parser = argparse.ArgumentParser(description="Piece Wise Linear Waveform Editor")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output to terminal"
    )
    args, unknown = parser.parse_known_args()

    app = QApplication([sys.argv[0]] + unknown)
    window = MainWindow(verbose=args.verbose)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()