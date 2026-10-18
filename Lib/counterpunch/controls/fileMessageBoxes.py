from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMessageBox, QStyle

from counterpunch.tools import platformSpecific


class MessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Question)
        self.setWindowTitle(QApplication.applicationName())
        self.setWindowModality(Qt.WindowModality.WindowModal)
        if platformSpecific.showAppIconInDialog():
            iconSize = self.style().pixelMetric(
                QStyle.PixelMetric.PM_MessageBoxIconSize, None, self
            )
            icon = self.windowIcon()
            size = icon.actualSize(QSize(iconSize, iconSize))
            self.setIconPixmap(icon.pixmap(size))


class ReloadMessageBox(MessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText(self.tr("Do you want to reload the document?"))
        self.setInformativeText(self.tr("Your current changes will be lost."))
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.setDefaultButton(QMessageBox.StandardButton.Yes)

    @classmethod
    def getReloadDocument(cls, parent, documentName=None):
        dialog = cls(parent)
        if documentName is not None:
            dialog.setText(
                dialog.tr("Do you want to reload “{}”?").format(documentName)
            )
        return dialog.exec()


class CloseMessageBox(MessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText(self.tr("Do you want to save your changes?"))
        self.setInformativeText(
            self.tr("Your changes will be lost if you don’t save them.")
        )
        self.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        self.setDefaultButton(QMessageBox.StandardButton.Save)

    @classmethod
    def getCloseDocument(cls, parent, documentName=None):
        dialog = cls(parent)
        if documentName is not None:
            dialog.setText(
                dialog.tr(
                    "Do you want to save the changes you made " "to “{}”?"
                ).format(documentName)
            )
        return dialog.exec()
