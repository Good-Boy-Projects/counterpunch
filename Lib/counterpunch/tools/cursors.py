"""
Cursors drawn in code, so they scale with the rest of the UI and need no
image files.
"""
from math import cos, radians, sin

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QCursor,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPixmap,
    QPolygonF,
)

_SIZE = 24
_CENTER = _SIZE / 2
# direction (degrees, y up) each corner of a transform box points to
_CORNER_ANGLES = {"tr": 45, "tl": 135, "bl": 225, "br": 315}
_cache = {}


def _stroked(path, width):
    stroker = QPainterPathStroker()
    stroker.setWidth(width)
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return stroker.createStroke(path)


def _point(radius, angle):
    a = radians(angle)
    return QPointF(_CENTER + radius * cos(a), _CENTER + radius * sin(a))


def _arrowHead(angle, ccw, radius, length=4.2, half=3.4):
    """Triangle at the arc end at *angle*, pointing along the arc."""
    a = radians(angle)
    base = _point(radius, angle)
    direction = (-sin(a), cos(a)) if ccw else (sin(a), -cos(a))
    normal = (cos(a), sin(a))
    tip = QPointF(base.x() + direction[0] * length, base.y() + direction[1] * length)
    left = QPointF(base.x() + normal[0] * half, base.y() + normal[1] * half)
    right = QPointF(base.x() - normal[0] * half, base.y() - normal[1] * half)
    path = QPainterPath()
    path.addPolygon(QPolygonF([tip, left, right]))
    path.closeSubpath()
    return path


def rotateCursor(corner="tr"):
    """
    A double-headed curved arrow that hugs the given corner ("tl", "tr", "br"
    or "bl") of a transform box. The hotspot is its center.
    """
    cursor = _cache.get(corner)
    if cursor is not None:
        return cursor
    theta = _CORNER_ANGLES.get(corner, 45)
    radius, span = 7.0, 38.0
    arc = QPainterPath()
    # Qt measures arc angles with y pointing down, hence the negation
    rect = (_CENTER - radius, _CENTER - radius, 2 * radius, 2 * radius)
    arc.arcMoveTo(*rect, -(theta - span))
    arc.arcTo(*rect, -(theta - span), -2 * span)
    black = _stroked(arc, 2.0)
    black.addPath(_arrowHead(theta + span, True, radius))
    black.addPath(_arrowHead(theta - span, False, radius))
    black = black.simplified()
    white = _stroked(black, 2.4).united(black)

    pixmap = QPixmap(_SIZE, _SIZE)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # glyph space is y-up
    painter.translate(0, _SIZE)
    painter.scale(1, -1)
    painter.fillPath(white, Qt.GlobalColor.white)
    painter.fillPath(black, Qt.GlobalColor.black)
    painter.end()
    cursor = QCursor(pixmap, int(_CENTER), int(_CENTER))
    _cache[corner] = cursor
    return cursor
