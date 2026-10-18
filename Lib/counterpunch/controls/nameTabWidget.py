from PySide6.QtWidgets import QTabWidget


class NameTabWidget(QTabWidget):
    def addNamedTab(self, tab):
        self.addTab(tab, tab.name)
