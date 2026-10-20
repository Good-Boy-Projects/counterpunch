import os

from fontTools.svgLib import SVGPath
from fontTools.ufoLib.glifLib import readGlyphFromString
from PySide6.QtCore import (
    QBuffer,
    QByteArray,
    QEvent,
    QIODevice,
    QObject,
    QPointF,
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QImage,
    QImageReader,
    QMouseEvent,
    QPainterPath,
    QPen,
    QPainterPathStroker,
    QTransform,
)
from PySide6.QtWidgets import QApplication

from defconQt.controls.glyphContextView import GlyphContextView, GlyphFlags
from defconQt.controls.glyphView import GlyphViewMinSizeForDetails
from counterpunch.drawingTools.baseTool import BaseTool
from counterpunch.objects import settings
from counterpunch.objects.layoutManager import LayoutManager
from counterpunch.tools import drawing, errorReports
from counterpunch.tools.cursors import rotateCursor
from counterpunch.tools.transformTools import (
    HANDLES,
    TransformSession,
    handlePoint,
    moveMatrix,
    rotateMatrix,
    scaleMatrix,
    selectionBounds,
    transformHit,
)
from counterpunch.tools.uiMethods import UIGlyphGuidelines

GlyphViewMinSizeForGrid = 10000
# sidebearing handles: size in screen pixels, hit radius in screen pixels
SidebearingHandleSize = 9
SidebearingHandleHitRadius = 8
SidebearingHandleColor = QColor(60, 120, 255, 210)
# transform box
TransformBoxColor = QColor(60, 120, 255)
TransformHandleSize = 8
_TransformScaleCursors = {
    "tl": Qt.CursorShape.SizeFDiagCursor,
    "br": Qt.CursorShape.SizeFDiagCursor,
    "tr": Qt.CursorShape.SizeBDiagCursor,
    "bl": Qt.CursorShape.SizeBDiagCursor,
    "t": Qt.CursorShape.SizeVerCursor,
    "b": Qt.CursorShape.SizeVerCursor,
    "l": Qt.CursorShape.SizeHorCursor,
    "r": Qt.CursorShape.SizeHorCursor,
}


class KeyEventFilter(QObject):
    def eventFilter(self, object, event):
        if event.type() == QEvent.Type.ShortcutOverride:
            # we'll only kang shortcut that do not have modifiers
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                event.accept()
                return True
        return False


class GlyphCanvasView(GlyphContextView):
    glyphNamesChanged = Signal()
    toolModified = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # needed so hovering (no button held) reaches mouseMoveEvent
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self._currentTool = BaseTool()
        self._currentToolActivated = False
        self._eventFilter = KeyEventFilter(self)
        font = self.window().font_()
        self._layoutManager = LayoutManager(font, self)
        self._mouseDown = False
        self._preview = False
        self._sidebearingDrag = None
        self._transformMode = False
        self._transformDrag = None
        self._overlayCursorShape = None

        self._defaultDrawingAttributes["showGlyphSelection"] = True

        # inbound notifications
        app = QApplication.instance()
        app.dispatcher.addObserver(self, "_needsUpdate", "glyphViewUpdate")
        app.dispatcher.addObserver(self, "_preferencesChanged", "preferencesChanged")

        self.readSettings()

    def readSettings(self):
        drawingAttributes = settings.drawingAttributes()
        for attr, value in drawingAttributes.items():
            self.setDefaultDrawingAttribute(attr, value)

    # --------------
    # Custom Methods
    # --------------

    def inputNames(self):
        return self._layoutManager.glyphList()

    def setInputNames(self, names):
        self._layoutManager.setGlyphList(names)

    def layoutManager(self):
        return self._layoutManager

    def setGlyphRecords(self, glyphRecords):
        # TODO: should we also NAK in mouseDown here?
        app = QApplication.instance()
        app.postNotification("glyphViewGlyphsWillChange")
        # TODO: secondly stop calling tool disabled when it's just
        # the glyph changing?
        # e.g. def toolGlyphWillChange(self, newGlyph)
        self._setCurrentToolEnabled(False)
        super().setGlyphRecords(glyphRecords)
        self._setCurrentToolEnabled(True)
        app.postNotification("glyphViewGlyphsChanged")
        self.glyphNamesChanged.emit()

    def previewEnabled(self):
        return self._preview

    def setPreviewEnabled(self, value):
        if value and self._mouseDown:
            return
        if value != self._preview:
            self._preview = value
            if value:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(self._currentTool.cursor)
            self.update()

    # -------------
    # Notifications
    # -------------

    def _subscribeToGlyphs(self, glyphRecords):
        super()._subscribeToGlyphs(glyphRecords)
        handledGlyphs = set()
        for glyphRecord in glyphRecords:
            glyph = glyphRecord.glyph
            if glyph in handledGlyphs:
                continue
            handledGlyphs.add(glyph)
            glyph.addObserver(self, "_glyphNameChanged", "Glyph.NameChanged")
            glyph.addObserver(self, "_glyphSelectionChanged", "Glyph.SelectionChanged")

    def _unsubscribeFromGlyphs(self):
        handledGlyphs = set()
        for glyphRecord in self._glyphRecords:
            glyph = glyphRecord.glyph
            if glyph in handledGlyphs:
                continue
            handledGlyphs.add(glyph)
            glyph.removeObserver(self, "Glyph.NameChanged")
            glyph.removeObserver(self, "Glyph.SelectionChanged")
        super()._unsubscribeFromGlyphs()

    def _glyphNameChanged(self, notification):
        self.glyphNamesChanged.emit()

    def _glyphSelectionChanged(self, notification):
        self.update()

    # app

    def _needsUpdate(self, notification):
        self.update()

    def _preferencesChanged(self, notification):
        self.readSettings()

    # ---------------
    # Display Control
    # ---------------

    def drawingAttribute(self, attr, flags):
        toolOverride = self._currentTool.drawingAttribute(attr, flags)
        if toolOverride is not None:
            return toolOverride
        return super().drawingAttribute(attr, flags)

    def drawingColor(self, attr, flags):
        toolOverride = self._currentTool.drawingColor(attr, flags)
        if toolOverride is not None:
            return toolOverride
        return super().drawingColor(attr, flags)

    # defaults

    def showSelection(self):
        return self.defaultDrawingAttribute("showGlyphSelection")

    def setShowSelection(self, value):
        self.setDefaultDrawingAttribute("showGlyphSelection", value)

    # ---------------
    # Drawing helpers
    # ---------------

    def drawGlyphBackground(self, painter, glyph, flags):
        if not self._preview:
            super().drawGlyphBackground(painter, glyph, flags)

    def drawBackground(self, painter, index):
        app = QApplication.instance()
        data = dict(widget=self, painter=painter, index=index)
        app.postNotification("glyphViewDrawBackground", data)
        self._currentTool.paintBackground(painter, index)

    def drawGlyphLayer(self, painter, glyph, flags):
        if self._preview:
            if flags.isActiveLayer:
                self.drawFillAndPoints(painter, glyph, flags)
        else:
            super().drawGlyphLayer(painter, glyph, flags)

    def drawForeground(self, painter, index):
        app = QApplication.instance()
        data = dict(widget=self, painter=painter, index=index)
        app.postNotification("glyphViewDrawForeground", data)
        self._currentTool.paint(painter, index)
        self._drawSidebearingHandles(painter, index)
        self._drawTransformBox(painter, index)

    # drawing primitives

    def drawMetrics(self, painter, glyph, flags):
        # TODO: should this have its own parameter?
        if self._impliedPointSize > GlyphViewMinSizeForGrid:
            viewportRect = (
                self.mapRectToCanvas(self.rect()).adjusted(0, 0, 2, 2).getRect()
            )
            drawing.drawGrid(painter, self._inverseScale, viewportRect)
        super().drawMetrics(painter, glyph, flags)

    def drawImage(self, painter, glyph, flags):
        drawing.drawGlyphImage(painter, glyph, self._inverseScale)

    def drawGuidelines(self, painter, glyph, flags):
        drawText = self._impliedPointSize > GlyphViewMinSizeForDetails
        viewportRect = self.mapRectToCanvas(self.rect()).getRect()
        if self.drawingAttribute("showFontGuidelines", flags):
            drawing.drawFontGuidelines(
                painter, glyph, self._inverseScale, viewportRect, drawText=drawText
            )
        if self.drawingAttribute("showGlyphGuidelines", flags):
            drawing.drawGlyphGuidelines(
                painter, glyph, self._inverseScale, viewportRect, drawText=drawText
            )

    def drawFillAndPoints(self, painter, glyph, flags):
        contourFillColor = self.drawingColor("contourFillColor", flags)
        componentFillColor = (
            contourFillColor
            if self._preview
            else self.drawingColor("componentFillColor", flags)
        )
        drawFill = self._preview or self.drawingAttribute("showGlyphFill", flags)
        drawComponentFill = self._preview or self.drawingAttribute(
            "showGlyphComponentFill", flags
        )
        drawSelection = not self._preview and self.drawingAttribute(
            "showGlyphSelection", flags
        )
        drawing.drawGlyphFillAndStroke(
            painter,
            glyph,
            self._inverseScale,
            contourFillColor=contourFillColor,
            componentFillColor=componentFillColor,
            drawFill=drawFill,
            drawComponentFill=drawComponentFill,
            drawSelection=drawSelection,
            drawStroke=False,
        )
        if self._preview or not self._impliedPointSize > GlyphViewMinSizeForDetails:
            return
        drawStartPoints = self.drawingAttribute("showGlyphStartPoints", flags)
        drawOnCurves = self.drawingAttribute("showGlyphOnCurvePoints", flags)
        drawOffCurves = self.drawingAttribute("showGlyphOffCurvePoints", flags)
        drawCoordinates = self.drawingAttribute("showGlyphPointCoordinates", flags)
        drawHandleCoordinates = self.drawingAttribute(
            "showGlyphBezierHandlesCoordinates", flags
        )
        drawCoordinatesOnSelection = self.drawingAttribute(
            "showGlyphCoordinatesWhenSelected", flags
        )
        drawing.drawGlyphPoints(
            painter,
            glyph,
            self._inverseScale,
            drawOnCurves=drawOnCurves,
            drawOffCurves=drawOffCurves,
            drawStartPoints=drawStartPoints,
            drawCoordinates=drawCoordinates,
            drawHandleCoordinates=drawHandleCoordinates,
            drawCoordinatesOnSelection=drawCoordinatesOnSelection,
            backgroundColor=self._backgroundColor,
        )

    def drawStroke(self, painter, glyph, flags):
        drawDetails = self._impliedPointSize > GlyphViewMinSizeForDetails
        drawStroke = self.drawingAttribute("showGlyphStroke", flags)
        drawComponentStroke = self.drawingAttribute("showGlyphComponentStroke", flags)
        drawing.drawGlyphFillAndStroke(
            painter,
            glyph,
            self._inverseScale,
            drawFill=False,
            drawComponentFill=False,
            drawStroke=drawStroke,
            drawComponentStroke=drawComponentStroke,
            drawSelection=False,
            partialAliasing=drawDetails,
        )

    def drawAnchors(self, painter, glyph, flags):
        if not self._impliedPointSize > GlyphViewMinSizeForDetails:
            return
        drawing.drawGlyphAnchors(painter, glyph, self._inverseScale)

    # ------------------
    # Sidebearing handles
    # ------------------

    def _sidebearingHandlesEnabled(self):
        return (
            not self._preview
            and getattr(self._currentTool, "showSidebearingHandles", False)
            and self._impliedPointSize > GlyphViewMinSizeForDetails
        )

    def _sidebearingHandles(self):
        """
        Returns (glyph, {"left": QPointF, "right": QPointF}) in canvas
        coordinates for the active glyph, or None.
        """
        glyph = self.activeGlyph()
        if glyph is None:
            return None
        y = -250
        font = glyph.font
        if font is not None and font.info.descender:
            y = font.info.descender
        return glyph, {
            "left": QPointF(0, y),
            "right": QPointF(glyph.width, y),
        }

    def _sidebearingHandleAt(self, canvasPos):
        pack = self._sidebearingHandles()
        if pack is None:
            return None
        glyph, handles = pack
        radius = SidebearingHandleHitRadius * self._inverseScale
        # right first, so a zero-width glyph can still be widened
        for side in ("right", "left"):
            pt = handles[side]
            if (
                abs(canvasPos.x() - pt.x()) <= radius
                and abs(canvasPos.y() - pt.y()) <= radius
            ):
                return side
        return None

    def _overlayCursorFor(self, canvasPos):
        if self._preview:
            return None
        pos = (canvasPos.x(), canvasPos.y())
        if self._transformMode:
            bounds = self._transformBounds()
            hit = (
                transformHit(bounds, pos, self._inverseScale)
                if bounds is not None
                else None
            )
            if hit is not None:
                kind, name = hit
                if kind == "scale":
                    return _TransformScaleCursors[name]
                if kind == "move":
                    return Qt.CursorShape.SizeAllCursor
                return "rotate:" + name
        if self._sidebearingHandlesEnabled():
            if self._sidebearingHandleAt(canvasPos) is not None:
                return Qt.CursorShape.SizeHorCursor
        return None

    def _updateOverlayCursor(self, canvasPos):
        shape = self._overlayCursorFor(canvasPos)
        if shape != self._overlayCursorShape:
            self._overlayCursorShape = shape
            if isinstance(shape, str):
                self.setCursor(rotateCursor(shape.split(":")[1]))
            elif shape is not None:
                self.setCursor(shape)
            else:
                self.setCursor(self._currentTool.cursor)

    def _drawSidebearingHandles(self, painter, index):
        if not self._sidebearingHandlesEnabled():
            return
        if index != self.activeIndex():
            return
        pack = self._sidebearingHandles()
        if pack is None:
            return
        _, handles = pack
        size = SidebearingHandleSize * self._inverseScale
        half = size / 2
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(SidebearingHandleColor)
        for pt in handles.values():
            path = QPainterPath()
            path.addRoundedRect(
                pt.x() - half, pt.y() - half, size, size, size / 4, size / 4
            )
            painter.drawPath(path)
        painter.restore()

    def _beginSidebearingDrag(self, side, event):
        glyph = self.activeGlyph()
        glyph.beginUndoGroup()
        self._sidebearingDrag = dict(
            side=side, glyph=glyph, startX=event.localPos().x(), applied=0
        )

    def _updateSidebearingDrag(self, event):
        drag = self._sidebearingDrag
        glyph = drag["glyph"]
        # measured in widget pixels, so relayout while dragging can't skew it
        target = round((event.localPos().x() - drag["startX"]) * self._inverseScale)
        delta = target - drag["applied"]
        if not delta:
            return
        if drag["side"] == "left":
            # contents follow the mouse, right sidebearing stays put
            glyph.move((delta, 0))
        glyph.width += delta
        drag["applied"] = target
        self.update()

    def _endSidebearingDrag(self):
        drag = self._sidebearingDrag
        self._sidebearingDrag = None
        drag["glyph"].endUndoGroup()
        self.update()

    # ------------
    # Transform box
    # ------------

    def transformMode(self):
        return self._transformMode

    def setTransformMode(self, value):
        value = bool(value)
        if value == self._transformMode:
            return
        if value and (self._preview or self._mouseDown):
            return
        self._transformMode = value
        if not value:
            self._overlayCursorShape = None
            self.setCursor(self._currentTool.cursor)
        self.update()

    def _transformBounds(self):
        glyph = self.activeGlyph()
        if glyph is None:
            return None
        bounds = selectionBounds(glyph)
        if bounds is None:
            return None
        xMin, yMin, xMax, yMax = bounds
        if xMax - xMin < 1e-6 and yMax - yMin < 1e-6:
            return None
        return bounds

    def _drawTransformBox(self, painter, index):
        if not self._transformMode or self._preview:
            return
        if index != self.activeIndex():
            return
        bounds = self._transformBounds()
        if bounds is None:
            return
        xMin, yMin, xMax, yMax = bounds
        size = TransformHandleSize * self._inverseScale
        half = size / 2
        painter.save()
        pen = QPen(TransformBoxColor)
        pen.setWidth(0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(xMin, yMin, xMax - xMin, yMax - yMin))
        painter.setBrush(QColor(255, 255, 255))
        for name in HANDLES:
            x, y = handlePoint(bounds, name)
            painter.drawRect(QRectF(x - half, y - half, size, size))
        painter.restore()

    def _beginTransformDrag(self, hit, canvasPos):
        glyph = self.activeGlyph()
        session = TransformSession(glyph)
        if not session.valid():
            return False
        session.begin()
        kind, name = hit
        self._transformDrag = dict(
            session=session,
            kind=kind,
            name=name,
            start=(canvasPos.x(), canvasPos.y()),
            bounds=session.bounds,
        )
        return True

    def _updateTransformDrag(self, event):
        drag = self._transformDrag
        canvasPos = self.mapToCanvas(event.localPos())
        pos = (canvasPos.x(), canvasPos.y())
        modifiers = event.modifiers()
        shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        alt = bool(modifiers & Qt.KeyboardModifier.AltModifier)
        kind = drag["kind"]
        if kind == "scale":
            matrix = scaleMatrix(drag["bounds"], drag["name"], pos, alt, shift)
        elif kind == "rotate":
            matrix = rotateMatrix(drag["bounds"], drag["start"], pos, shift)
        else:
            matrix = moveMatrix(drag["start"], pos, shift)
        drag["session"].apply(matrix)
        self.update()

    def _endTransformDrag(self):
        drag = self._transformDrag
        self._transformDrag = None
        drag["session"].end()
        self.update()

    # ---------------
    # QWidget methods
    # ---------------

    def showEvent(self, event):
        super().showEvent(event)
        self._setCurrentToolEnabled(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self._setCurrentToolEnabled(False)
        self._preview = False
        self._transformMode = False

    def closeEvent(self, event):
        super().closeEvent(event)
        if event.isAccepted():
            self._setCurrentToolEnabled(False)
            app = QApplication.instance()
            app.dispatcher.removeObserver(self, "glyphViewUpdate")
            app.dispatcher.removeObserver(self, "parametersChanged")

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            url = mimeData.urls()[0]
            if url.isLocalFile():
                path = url.toLocalFile()
                ext = os.path.splitext(path)[1][1:]
                formats = QImageReader.supportedImageFormats() + ["glif"]
                if ext.lower() in formats:
                    event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            paths = mimeData.urls()
            # pick just one image
            path = paths[0].toLocalFile()
            fileName = os.path.basename(path)
            with open(path, "rb") as imgFile:
                data = imgFile.read()
            ext = os.path.splitext(path)[1][1:]
            # TODO: make sure we cleanup properly when replacing an image with
            # another
            if ext.lower() == "glif":
                otherGlyph = self._glyph.__class__()
                try:
                    readGlyphFromString(data, otherGlyph, otherGlyph.getPointPen())
                except Exception as e:
                    errorReports.showCriticalException(e)
                    return
                self._glyph.beginUndoGroup()
                otherGlyph.drawPoints(self._glyph.getPointPen())
                self._glyph.endUndoGroup()
                return
            if ext.lower() == "svg":
                try:
                    svgPath = SVGPath.fromstring(data)
                except Exception as e:
                    errorReports.showCriticalException(e)
                    return
                self._glyph.beginUndoGroup()
                svgPath.draw(self._glyph.getPen())
                self._glyph.endUndoGroup()
                return
            if ext.lower() != "png":
                # convert
                img = QImage(path)
                data = QByteArray()
                buffer = QBuffer(data)
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                img.save(buffer, "PNG")
                # format
                data = bytearray(data)
                fileName = "%s.png" % os.path.splitext(fileName)[0]
            imageSet = self._glyph.font.images
            try:
                imageSet[fileName] = data
            except Exception as e:
                errorReports.showCriticalException(e)
                return
            image = self._glyph.instantiateImage()
            image.fileName = fileName
            self._glyph.image = image
            event.setAccepted(True)
        else:
            super().dropEvent(event)

    def contextMenuEvent(self, event):
        self._redirectEvent(event, self._currentTool.contextMenuEvent, True)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        # TODO: sending an event that doesn't contain the menu isn't
        # extremely useful
        app.postNotification("glyphViewContextMenu", data)

    def keyPressEvent(self, event):
        # Hold ` (backtick/tilde key, unshifted) to preview the filled
        # glyph, RoboFont-style. Handled here, before tool redirection, so
        # it works regardless of which drawing tool is currently active.
        if not event.isAutoRepeat() and event.key() == Qt.Key.Key_QuoteLeft:
            self.setPreviewEnabled(True)
            event.accept()
            return
        if self._transformMode and self._transformDrag is None:
            if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.setTransformMode(False)
                event.accept()
                return
        # TODO: put this in event filter?
        if self._currentTool.grabKeyboard and event.key() == Qt.Key.Key_Escape:
            ok = self.setCurrentTool(self._previousTool)
            if ok:
                self.toolModified.emit(self._previousTool)
        # Note: not needed, only for parity with keyReleaseEvent
        if not self._currentTool.grabKeyboard and event.key() == Qt.Key.Key_Space:
            event.ignore()
            return
        self._redirectEvent(event, self._currentTool.keyPressEvent)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        app.postNotification("glyphViewKeyPress", data)

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat() and event.key() == Qt.Key.Key_QuoteLeft:
            self.setPreviewEnabled(False)
            event.accept()
            return
        # TODO: I don't know why we have to do this for releaseEvent
        if not self._currentTool.grabKeyboard and event.key() == Qt.Key.Key_Space:
            event.ignore()
            return
        self._redirectEvent(event, self._currentTool.keyReleaseEvent)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        app.postNotification("glyphViewKeyRelease", data)

    def mousePressEvent(self, event):
        self._mouseDown = True
        if self._preview:
            self._panOrigin = event.globalPos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            canvasPos = self.mapToCanvas(event.localPos())
            if self._transformMode:
                bounds = self._transformBounds()
                hit = (
                    transformHit(
                        bounds, (canvasPos.x(), canvasPos.y()), self._inverseScale
                    )
                    if bounds is not None
                    else None
                )
                if hit is not None and self._beginTransformDrag(hit, canvasPos):
                    return
            if self._sidebearingHandlesEnabled():
                side = self._sidebearingHandleAt(canvasPos)
                if side is not None:
                    self._beginSidebearingDrag(side, event)
                    return
            if self._transformMode:
                # clicked away from the box: leave transform mode and let the
                # current tool handle the click
                self.setTransformMode(False)
        self._redirectEvent(event, self._currentTool.mousePressEvent, True)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        app.postNotification("glyphViewMousePress", data)

    def mouseMoveEvent(self, event):
        if self._preview and hasattr(self, "_panOrigin"):
            pos = event.globalPos()
            self.scrollBy(pos - self._panOrigin)
            self._panOrigin = pos
            return
        if self._transformDrag is not None:
            self._updateTransformDrag(event)
            return
        if self._sidebearingDrag is not None:
            self._updateSidebearingDrag(event)
            return
        if not event.buttons() & Qt.MouseButton.LeftButton:
            self._updateOverlayCursor(self.mapToCanvas(event.localPos()))
        self._redirectEvent(event, self._currentTool.mouseMoveEvent, True)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        app.postNotification("glyphViewMouseMove", data)

    def mouseReleaseEvent(self, event):
        if self._transformDrag is not None:
            if event.button() == Qt.MouseButton.LeftButton:
                self._endTransformDrag()
                self._mouseDown = False
            return
        if self._sidebearingDrag is not None:
            if event.button() == Qt.MouseButton.LeftButton:
                self._endSidebearingDrag()
                self._mouseDown = False
            return
        self._redirectEvent(event, self._currentTool.mouseReleaseEvent, True)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        app.postNotification("glyphViewMouseRelease", data)
        if hasattr(self, "_panOrigin"):
            if self._preview:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            del self._panOrigin
        self._mouseDown = False

    def mouseDoubleClickEvent(self, event):
        self._redirectEvent(event, self._currentTool.mouseDoubleClickEvent, True)
        app = QApplication.instance()
        data = dict(event=event, widget=self)
        app.postNotification("glyphViewMouseDoubleClick", data)

    # ------------
    # Canvas tools
    # ------------

    # current tool

    def _setCurrentToolEnabled(self, value):
        if self._currentToolActivated == value:
            return
        self._currentToolActivated = value
        if value:
            self._currentTool.toolActivated()
            if self._currentTool.grabKeyboard:
                self.window().installEventFilter(self._eventFilter)
        else:
            if self._currentTool.grabKeyboard:
                self.window().removeEventFilter(self._eventFilter)
            self._currentTool.toolDisabled()

    def currentTool(self):
        return self._currentTool

    def setCurrentTool(self, tool):
        if self._mouseDown:
            return False
        self._setCurrentToolEnabled(False)
        if tool.grabKeyboard:
            self._previousTool = self._currentTool
        self._currentTool = tool
        self.setTransformMode(False)
        self._overlayCursorShape = None
        self.setCursor(tool.cursor)
        self._setCurrentToolEnabled(True)
        return True

    def _redirectEvent(self, event, callback, transmute=False):
        if self._preview:
            return
        # construct a new event with pos in canvas coordinates
        if transmute:
            if isinstance(event, QContextMenuEvent):
                canvasPos = self.mapToCanvas(event.pos())
                event = event.__class__(
                    event.reason(), canvasPos, event.globalPos(), event.modifiers()
                )
                event.localPos = lambda: canvasPos
            elif isinstance(event, QMouseEvent):
                # TODO: not redirect mouse events if there's no glyph?
                # if not self._glyphRecords:
                #     return
                canvasPos = self.mapToCanvas(event.localPos())
                event = event.__class__(
                    event.type(),
                    canvasPos,
                    event.windowPos(),
                    event.screenPos(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                )
            else:
                raise ValueError(f"cannot transmute event: {event}")
        callback(event)

    # items location

    def _itemsAt(self, func, obj, justOne=True):
        """
        Go through all anchors, points and components (in this order) in the
        glyph, construct their canvas path and list items for which
        *func(path, obj)* returns True, or only return the first item if
        *justOne* is set to True.

        An item is a (contour, index) or (element, None) tuple. Point objects
        aren't returned directly because their usefulness is limited barring
        their parent contour.

        Here is a sample *func* function that tests whether item with path
        *path* contains *pos*:

            def myFunction(path, pos):
                return path.contains(pos)

        This is useful to find out whether an item was clicked on canvas.
        """
        scale = self._inverseScale
        # TODO: export this from drawing or use QSettings.
        # XXX: outdated
        # anchor
        anchorSize = 7 * scale
        anchorHalfSize = anchorSize / 2
        # offCurve
        offSize = 5 * scale
        offHalf = offSize / 2
        offStrokeWidth = 2.5 * scale
        # onCurve
        onSize = 6.5 * scale
        onHalf = onSize / 2
        onStrokeWidth = 1.5 * scale
        # onCurve smooth
        smoothSize = 8 * scale
        smoothHalf = smoothSize / 2
        # guideline pt
        guidelineStrokeWidth = 1 * scale

        if not justOne:
            ret = dict(anchors=[], points=[], components=[], guidelines=[], image=None)
        if self._glyph is None:
            if justOne:
                return None
            return ret
        flags = GlyphFlags(True)
        # anchors
        if self.drawingAttribute("showGlyphAnchors", flags):
            for anchor in reversed(self._glyph.anchors):
                path = QPainterPath()
                path.addEllipse(
                    anchor.x - anchorHalfSize,
                    anchor.y - anchorHalfSize,
                    anchorSize,
                    anchorSize,
                )
                if func(path, obj):
                    if justOne:
                        return anchor
                    ret["anchors"].append(anchor)
        # points
        if self.drawingAttribute("showGlyphOnCurvePoints", flags):
            for contour in reversed(self._glyph):
                for index, point in enumerate(contour):
                    path = QPainterPath()
                    if point.segmentType is None:
                        x = point.x - offHalf
                        y = point.y - offHalf
                        path.addEllipse(x, y, offSize, offSize)
                        strokeWidth = offStrokeWidth
                    else:
                        if point.smooth:
                            x = point.x - smoothHalf
                            y = point.y - smoothHalf
                            path.addEllipse(x, y, smoothSize, smoothSize)
                        else:
                            x = point.x - onHalf
                            y = point.y - onHalf
                            path.addRect(x, y, onSize, onSize)
                        strokeWidth = onStrokeWidth
                    path = _shapeFromPath(path, strokeWidth)
                    if func(path, obj):
                        if justOne:
                            return (contour, index)
                        ret["points"].append((contour, index))
        # components
        for component in reversed(self._glyph.components):
            path = component.getRepresentation("TruFont.QPainterPath")
            if func(path, obj):
                if justOne:
                    return component
                ret["components"].append(component)
        # guideline
        # TODO: we should further dispatch with showFontGuidelines,
        # although both are bind in the UI
        if self.drawingAttribute("showGlyphGuidelines", flags):
            for guideline in UIGlyphGuidelines(self._glyph):
                if None not in (guideline.x, guideline.y):
                    # point
                    x = guideline.x - smoothHalf
                    y = guideline.y - smoothHalf
                    path = QPainterPath()
                    path.addEllipse(x, y, smoothSize, smoothSize)
                    path = _shapeFromPath(path, guidelineStrokeWidth)
                    if func(path, obj):
                        if justOne:
                            return guideline
                        ret["guidelines"].append(guideline)
                    # TODO: catch line if selected
        # image
        if self.drawingAttribute("showGlyphImage", flags):
            image = self._glyph.image
            pixmap = image.getRepresentation("defconQt.QPixmap")
            if pixmap is not None:
                path = QPainterPath()
                transform = QTransform(*image.transformation)
                rect = transform.mapRect(QRectF(pixmap.rect()))
                path.addRect(*rect.getCoords())
                if func(path, obj):
                    if justOne:
                        return image
                    ret["image"] = image
        if not justOne:
            return ret
        return None

    def itemAt(self, pos):
        """
        Find one item at *pos*.

        An item is a (point, contour) or (anchor, None) or (component, None)
        tuple.
        """
        return self.itemsAt(pos, True)

    def itemsAt(self, pos, items=False):
        """
        Find items at *pos*.
        """
        return self._itemsAt(lambda path, pos: path.contains(pos), pos, items)

    def items(self, rect):
        """
        Find items that intersect with *rect* (can be any QPainterPath).
        """
        return self._itemsAt(lambda path, rect: path.intersects(rect), rect, False)


def _shapeFromPath(path, width):
    if path.isEmpty():
        return path
    ps = QPainterPathStroker()
    ps.setWidth(width)
    p = ps.createStroke(path)
    p.addPath(path)
    return p