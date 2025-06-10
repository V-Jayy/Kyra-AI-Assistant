"""Qt signal bus for thread-safe logging."""

from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """Global signals for transcript and command events."""

    transcript = pyqtSignal(str)
    command = pyqtSignal(dict)


BUS = SignalBus()
