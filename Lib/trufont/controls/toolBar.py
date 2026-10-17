from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPainterPath
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from trufont.controls.pathButton import PathButton


def metricsIcon():
    """Metrics button icon: 28x28, y axis up like the tool icons."""
    path = QPainterPath()
    path.moveTo(12, 17.77)
    path.lineTo(12, 27.5)
    path.cubicTo(12, 27.78, 12.22, 28, 12.5, 28)
    path.lineTo(15.5, 28)
    path.cubicTo(15.78, 28, 16, 27.78, 16, 27.5)
    path.lineTo(16, 17.77)
    path.cubicTo(15.39, 17.92, 14.72, 18, 14, 18)
    path.cubicTo(13.28, 18, 12.61, 17.92, 12, 17.77)
    path.closeSubpath()
    path.moveTo(18, 15)
    path.cubicTo(18, 16.1, 16.21, 17, 14, 17)
    path.cubicTo(11.79, 17, 10, 16.1, 10, 15)
    path.cubicTo(10, 14.51, 10.37, 14.06, 10.96, 13.71)
    path.lineTo(10, 5.84)
    path.cubicTo(9.95, 5.43, 10.25, 5.05, 10.66, 5.01)
    path.cubicTo(10.69, 5, 10.72, 5, 10.75, 5)
    path.cubicTo(11.12, 5, 11.45, 5.28, 11.49, 5.66)
    path.lineTo(11.78, 8)
    path.lineTo(16.22, 8)
    path.lineTo(16.51, 5.66)
    path.cubicTo(16.55, 5.28, 16.88, 5, 17.25, 5)
    path.cubicTo(17.28, 5, 17.31, 5, 17.34, 5.01)
    path.cubicTo(17.75, 5.06, 18.05, 5.43, 18, 5.84)
    path.lineTo(17.03, 13.71)
    path.cubicTo(17.63, 14.06, 18, 14.5, 18, 15)
    path.lineTo(18, 15)
    path.lineTo(18, 15)
    path.closeSubpath()
    path.moveTo(15.97, 10)
    path.lineTo(12.02, 10)
    path.lineTo(12.41, 13.17)
    path.cubicTo(12.9, 13.06, 13.43, 13, 14, 13)
    path.cubicTo(14.57, 13, 15.1, 13.06, 15.58, 13.16)
    path.lineTo(15.97, 10)
    path.closeSubpath()
    path.moveTo(28, 7.08)
    path.lineTo(28, 0)
    path.lineTo(0, 0)
    path.lineTo(0, 7.08)
    path.lineTo(9.46, 9.59)
    path.lineTo(9.02, 5.96)
    path.cubicTo(8.96, 5.5, 9.09, 5.04, 9.37, 4.67)
    path.cubicTo(9.66, 4.3, 10.08, 4.07, 10.54, 4.01)
    path.lineTo(10.69, 4)
    path.lineTo(10.75, 4)
    path.cubicTo(11.64, 4, 12.38, 4.66, 12.49, 5.53)
    path.lineTo(12.67, 7)
    path.lineTo(15.34, 7)
    path.lineTo(15.52, 5.53)
    path.cubicTo(15.62, 4.66, 16.37, 4, 17.25, 4)
    path.lineTo(17.4, 4)
    path.lineTo(17.46, 4.01)
    path.cubicTo(17.93, 4.07, 18.34, 4.3, 18.63, 4.67)
    path.cubicTo(18.92, 5.04, 19.05, 5.5, 18.99, 5.96)
    path.lineTo(18.54, 9.59)
    path.lineTo(28, 7.08)
    path.closeSubpath()
    path.moveTo(9.73, 13.41)
    path.lineTo(0, 10.98)
    path.lineTo(0, 12.52)
    path.lineTo(3.25, 13.34)
    path.lineTo(3.25, 16.79)
    path.lineTo(0, 15.98)
    path.lineTo(0, 17.52)
    path.lineTo(3.25, 18.34)
    path.lineTo(3.25, 21.79)
    path.lineTo(0, 20.98)
    path.lineTo(0, 22.52)
    path.lineTo(11, 25.27)
    path.lineTo(11, 23.73)
    path.lineTo(4.75, 22.16)
    path.lineTo(4.75, 18.71)
    path.lineTo(11, 20.27)
    path.lineTo(11, 18.73)
    path.lineTo(4.75, 17.16)
    path.lineTo(4.75, 13.71)
    path.lineTo(9.02, 14.77)
    path.cubicTo(9.06, 14.4, 9.23, 13.9, 9.73, 13.4)
    path.lineTo(9.73, 13.4)
    path.lineTo(9.73, 13.41)
    path.closeSubpath()
    path.moveTo(18.98, 14.78)
    path.lineTo(23.25, 13.71)
    path.lineTo(23.25, 17.16)
    path.lineTo(17, 18.73)
    path.lineTo(17, 20.27)
    path.lineTo(23.25, 18.71)
    path.lineTo(23.25, 22.16)
    path.lineTo(17, 23.73)
    path.lineTo(17, 25.27)
    path.lineTo(28, 22.52)
    path.lineTo(28, 20.98)
    path.lineTo(24.75, 21.79)
    path.lineTo(24.75, 18.34)
    path.lineTo(28, 17.52)
    path.lineTo(28, 15.98)
    path.lineTo(24.75, 16.79)
    path.lineTo(24.75, 13.34)
    path.lineTo(28, 12.52)
    path.lineTo(28, 10.98)
    path.lineTo(18.27, 13.41)
    path.cubicTo(18.77, 13.9, 18.94, 14.41, 18.98, 14.78)
    path.lineTo(18.98, 14.78)
    path.closeSubpath()
    path.setFillRule(Qt.FillRule.WindingFill)
    return path


# kept so existing imports keep working
metricsPlaceholderIcon = metricsIcon


class ToolBar(QWidget):
    """
    TODO: allow all orientations
    """

    currentToolChanged = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(90, 90, 90)
        self._selectedColor = QColor(20, 146, 230)
        self._currentTool = 0
        self._tools = []
        # (name, icon, callback, after) buttons that run a command instead of
        # selecting a drawing tool. Shown among the tools.
        self._actions = []
        self._toolButtons = []
        self._actionButtons = []

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(12)

    def _buttonClicked(self):
        sender = self.sender()
        toolIndex = 0
        for i, btn in enumerate(self._toolButtons):
            if btn == sender:
                color = self._selectedColor
                toolIndex = i
            else:
                color = self._color
            cmds = btn.drawingCommands()
            cmds[1][2] = color
            btn.setDrawingCommands(cmds)
        self._currentTool = toolIndex
        self.currentToolChanged.emit(self._tools[toolIndex])

    def _updateColors(self):
        for i, btn in enumerate(self._toolButtons):
            if self._currentTool == i:
                color = self._selectedColor
            else:
                color = self._color
            cmds = btn.drawingCommands()
            cmds[1][2] = color
            btn.setDrawingCommands(cmds)
        for btn in self._actionButtons:
            cmds = btn.drawingCommands()
            cmds[1][2] = self._color
            btn.setDrawingCommands(cmds)

    def _makeActionButton(self, name, icon, callback):
        btn = PathButton(self)
        btn.setDrawingCommands([QSize(28, 28), [icon, "f", self._color]])
        btn.setIsDownColor(QColor())
        btn.setIsFlipped(True)
        btn.setToolTip(name)
        # does not change the current tool
        btn.clicked.connect(lambda *args, cb=callback: cb())
        return btn

    def _updateTools(self):
        layout = self.layout()
        for i in reversed(range(layout.count())):
            layout.takeAt(i).widget().close()
        self._toolButtons = []
        self._actionButtons = []
        toolNames = [tool.name for tool in self._tools]
        # actions whose "after" tool doesn't exist go after the last tool
        trailing = [
            action
            for action in self._actions
            if action[3] is None or action[3] not in toolNames
        ]
        for index, tool in enumerate(self._tools):
            btn = PathButton(self)
            if index == self._currentTool:
                color = self._selectedColor
            else:
                color = self._color
            btn.setDrawingCommands([QSize(28, 28), [tool.icon, "f", color]])
            btn.setIsDownColor(QColor())
            btn.setIsFlipped(True)
            text = tool.name
            if tool.shortcut is not None:
                text = f"{text} ({tool.shortcut})"
                btn.setShortcut(QKeySequence(tool.shortcut))
            btn.setToolTip(text)
            btn.clicked.connect(self._buttonClicked)
            layout.addWidget(btn)
            self._toolButtons.append(btn)
            for name, icon, callback, after in self._actions:
                if after == tool.name:
                    actionBtn = self._makeActionButton(name, icon, callback)
                    layout.addWidget(actionBtn)
                    self._actionButtons.append(actionBtn)
        for name, icon, callback, after in trailing:
            actionBtn = self._makeActionButton(name, icon, callback)
            layout.addWidget(actionBtn)
            self._actionButtons.append(actionBtn)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

    def addActionButton(self, name, icon, callback, after=None):
        """
        Adds a button that calls ``callback()`` when clicked, without becoming
        the current tool. ``icon`` is a QPainterPath in 28x28 coordinates.
        The button is placed right below the tool called ``after``; if that is
        None or not found, it goes below the last tool.
        """
        self._actions.append((name, icon, callback, after))
        self._updateTools()

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = color
        self._updateColors()

    def selectedColor(self):
        return self._color

    def setSelectedColor(self, color):
        self._selectedColor = color
        self._updateColors()

    def tools(self):
        return self._tools

    def setTools(self, tools):
        self._tools = list(tools)
        self._updateTools()

    def addTool(self, tool):
        self._tools.append(tool)
        self._updateTools()

    def removeTool(self, tool):
        self._tools.remove(tool)
        self._updateTools()

    def currentTool(self):
        return self._tools[self._currentTool]

    def setCurrentTool(self, tool):
        self._currentTool = self._tools.index(tool)
        self._updateColors()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(240, 240, 240))