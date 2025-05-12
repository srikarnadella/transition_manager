import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

from ui_main import SongTransitionApp

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    dark = QPalette()
    dark.setColor(QPalette.Window, QColor(53,53,53))
    dark.setColor(QPalette.WindowText, Qt.white)
    dark.setColor(QPalette.Base, QColor(25,25,25))
    dark.setColor(QPalette.AlternateBase, QColor(53,53,53))
    dark.setColor(QPalette.ToolTipBase, Qt.white)
    dark.setColor(QPalette.ToolTipText, Qt.white)
    dark.setColor(QPalette.Text, Qt.white)
    dark.setColor(QPalette.Button, QColor(53,53,53))
    dark.setColor(QPalette.ButtonText, Qt.white)
    dark.setColor(QPalette.BrightText, Qt.red)
    dark.setColor(QPalette.Link, QColor(42,130,218))
    dark.setColor(QPalette.Highlight, QColor(42,130,218))
    dark.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark)

    window = SongTransitionApp()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())
