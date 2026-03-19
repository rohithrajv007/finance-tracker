import sys
import os

# fix sys.stderr/stdout being None in PyInstaller console=False mode
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')

import faulthandler
try:
    faulthandler.enable()
except Exception:
    pass

from PyQt6.QtWidgets import (
    QApplication, QScrollArea,
    QTableWidget, QAbstractItemView
)
from PyQt6.QtCore import (
    QObject, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import QWheelEvent


class SmoothScroll(QObject):
    def __init__(self, widget, speed=4, duration=180):
        super().__init__(widget)
        self._widget    = widget
        self._speed     = speed
        self._duration  = duration
        self._target    = 0
        self._animation = None

        if isinstance(widget, QTableWidget):
            widget.setVerticalScrollMode(
                QAbstractItemView.ScrollMode.ScrollPerPixel
            )

        widget.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if isinstance(event, QWheelEvent):
            delta     = event.angleDelta().y()
            scrollbar = self._widget.verticalScrollBar()

            self._target = max(
                scrollbar.minimum(),
                min(
                    scrollbar.maximum(),
                    scrollbar.value() - delta * self._speed // 10
                )
            )

            if self._animation and \
               self._animation.state() == QPropertyAnimation.State.Running:
                self._animation.stop()

            self._animation = QPropertyAnimation(scrollbar, b"value")
            self._animation.setDuration(self._duration)
            self._animation.setStartValue(scrollbar.value())
            self._animation.setEndValue(self._target)
            self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._animation.start()
            return True
        return False


def apply_smooth_scroll(window):
    for widget in window.findChildren(QScrollArea):
        SmoothScroll(widget, speed=4, duration=180)
    for widget in window.findChildren(QTableWidget):
        SmoothScroll(widget, speed=4, duration=150)


def handle_exception(exc_type, exc_value, exc_traceback):
    import traceback
    try:
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    except Exception:
        pass


sys.excepthook = handle_exception

from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    apply_smooth_scroll(window)
    window.show()
    sys.exit(app.exec())