import sys
import traceback

from PySide6.QtWidgets import QMessageBox

_showMessages = True


def showCriticalException(e, message=None):
    _prepareException(e, QMessageBox.Icon.Critical, message)


def showWarningException(e, message=None):
    _prepareException(e, QMessageBox.Icon.Warning, message)


def exceptionCallback(etype, value, tb):
    title = ":("
    message = "Counterpunch has encountered a problem and must shutdown."
    _displayException(etype, value, tb, QMessageBox.Icon.Critical, title, message)


def _displayException(etype, value, tb, kind, title, message):
    global _showMessages
    exc = traceback.format_exception(etype, value, tb)
    exc_text = "".join(exc)
    print(exc_text, file=sys.stderr)
    print(exc_text, file=sys.__stderr__, flush=True)

    if _showMessages:
        messageBox = QMessageBox(kind, title, message)
        standardButtons = QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Close
        if kind == QMessageBox.Icon.Critical:
            standardButtons |= QMessageBox.StandardButton.Ignore
        messageBox.setStandardButtons(standardButtons)
        messageBox.setDetailedText(exc_text)
        messageBox.setInformativeText(str(value))
        result = messageBox.exec()
        if result == QMessageBox.StandardButton.Close:
            sys.exit(1)
        elif result == QMessageBox.StandardButton.Ignore:
            _showMessages = False


def _prepareException(e, kind, message):
    title = e.__class__.__name__
    _displayException(e.__class__, e, e.__traceback__, kind, title, message)