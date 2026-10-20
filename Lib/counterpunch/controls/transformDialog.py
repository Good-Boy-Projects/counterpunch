from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QVBoxLayout,
)

def _spin(minimum, maximum, value, decimals=2, suffix=""):
    box = QDoubleSpinBox()
    box.setDecimals(decimals)
    box.setRange(minimum, maximum)
    box.setValue(value)
    box.setSuffix(suffix)
    box.setKeyboardTracking(False)
    return box


class TransformDialog(QDialog):
    def __init__(self, parent=None, hasSelection=False):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Transform"))
        self.setWindowModality(Qt.WindowModality.WindowModal)

        self.originBox = QComboBox()
        self.originBox.addItems(
            [
                self.tr("Center of selection")
                if hasSelection
                else self.tr("Center of glyph"),
                self.tr("Bottom left"),
                self.tr("Glyph origin (0, 0)"),
            ]
        )
        self.moveX = _spin(-100000, 100000, 0)
        self.moveY = _spin(-100000, 100000, 0)
        self.scaleX = _spin(-10000, 10000, 100, suffix=" %")
        self.scaleY = _spin(-10000, 10000, 100, suffix=" %")
        self.linkScale = QCheckBox(self.tr("Scale proportionally"))
        self.linkScale.setChecked(True)
        self.rotate = _spin(-360, 360, 0, suffix="°")
        self.skew = _spin(-89, 89, 0, suffix="°")
        self.roundBox = QCheckBox(self.tr("Round to integers"))
        self.roundBox.setChecked(True)

        self.scaleX.valueChanged.connect(self._scaleXChanged)

        layout = QFormLayout()
        layout.addRow(self.tr("Origin:"), self.originBox)
        layout.addRow(self.tr("Move X:"), self.moveX)
        layout.addRow(self.tr("Move Y:"), self.moveY)
        layout.addRow(self.tr("Scale X:"), self.scaleX)
        layout.addRow(self.tr("Scale Y:"), self.scaleY)
        layout.addRow("", self.linkScale)
        layout.addRow(self.tr("Rotate:"), self.rotate)
        layout.addRow(self.tr("Skew:"), self.skew)
        layout.addRow("", self.roundBox)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main = QVBoxLayout(self)
        main.addLayout(layout)
        main.addWidget(buttons)
        self.moveX.setFocus()

    def _scaleXChanged(self, value):
        if self.linkScale.isChecked():
            self.scaleY.setValue(value)

    def values(self):
        return dict(
            originMode=self.originBox.currentIndex(),
            move=(self.moveX.value(), self.moveY.value()),
            scale=(self.scaleX.value() / 100, self.scaleY.value() / 100),
            rotate=self.rotate.value(),
            skew=self.skew.value(),
            rounding=self.roundBox.isChecked(),
        )

    @classmethod
    def getTransform(cls, parent=None, hasSelection=False):
        dialog = cls(parent, hasSelection)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.values()
