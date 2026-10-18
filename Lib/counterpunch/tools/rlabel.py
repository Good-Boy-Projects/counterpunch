from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


# A QLabel for right-aligning text to edit boxes to cut down repetition.
class RLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )