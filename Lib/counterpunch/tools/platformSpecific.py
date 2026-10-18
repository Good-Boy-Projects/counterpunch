import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence

# -----------
# File dialog
# -----------


def treatPackageAsFile():
    return sys.platform == "darwin"


# -----
# Fonts
# -----


def fontSizeDelta():
    return int(sys.platform == "darwin")


def UIFontOverride():
    if sys.platform == "win32":
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        return font
    return None


# -------------
# Key sequences
# -------------


def altDeleteSequence():
    if sys.platform == "darwin":
        return "Backspace"
    return None


def altRedoSequence():
    if sys.platform == "win32":
        return "Ctrl+Shift+Z"
    return None


def closeKeySequence():
    if sys.platform == "win32":
        return "Ctrl+W"
    return QKeySequence.StandardKey.Close


def previousTabSequence():
    if sys.platform == "win32":
        return "Ctrl+Shift+Tab"
    return QKeySequence.StandardKey.PreviousChild


def combinedModifiers():
    # on Windows, Ctrl+Alt is reserved by the system. use WinKey+Alt
    if sys.platform == "win32":
        return Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.AltModifier
    return Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier


def isDeleteEvent(event):
    if event.matches(QKeySequence.StandardKey.Delete):
        return True
    if sys.platform == "darwin" and event.key() == Qt.Key.Key_Backspace:
        return True
    modifiers = event.modifiers()
    if (
        modifiers & Qt.KeyboardModifier.ShiftModifier
        or modifiers & Qt.KeyboardModifier.AltModifier
    ):
        modifiers_ = (
            modifiers
            & ~Qt.KeyboardModifier.ShiftModifier
            & ~Qt.KeyboardModifier.AltModifier
        )
        event_ = event.__class__(
            event.type(),
            event.key(),
            modifiers_,
            event.text(),
            event.isAutoRepeat(),
            event.count(),
        )
        return event_.matches(QKeySequence.StandardKey.Delete)
    return False


# -------
# Margins
# -------


def needsTighterMargins():
    return sys.platform == "darwin"


def widen():
    return sys.platform == "win32"


# --------
# Menu bar
# --------


def useGlobalMenuBar():
    if sys.platform == "darwin":
        return True
    elif sys.platform.startswith("linux"):
        env = os.environ
        if (
            env.get("XDG_CURRENT_DESKTOP") == "Unity"
            and len(env.get("UBUNTU_MENUPROXY", "")) > 1
        ):
            return True
    return False


def mergeOpenAndImport():
    return sys.platform == "darwin"


def windowCommandsInMenu():
    return sys.platform == "darwin"


def setAppName():
    if sys.platform == "darwin":
        try:
            from Foundation import NSBundle

            bundle = NSBundle.mainBundle()
            if bundle:
                app_info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if app_info:
                    app_info["CFBundleName"] = "Counterpunch"
        except ImportError as e:
            print(f"Could not set title: {e}")
            pass


# -----------
# Main window
# -----------


def appNameInTitle():
    if sys.platform == "darwin":
        return False
    return True


def shouldSpawnDocument():
    return sys.platform != "darwin"


# -----------
# Message box
# -----------


def showAppIconInDialog():
    return sys.platform == "darwin"


# -----------
# Rubber band
# -----------


def useBuiltinRubberBand():
    return sys.platform == "darwin"


# ----------
# Stylesheet
# ----------


def appStyleSheet():
    if sys.platform == "win32":
        return "QStatusBar::item { border: none; }"
    elif sys.platform == "darwin":
        return "QToolTip { background-color: white; }"
    return None