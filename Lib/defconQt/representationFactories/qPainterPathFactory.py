"""
The *qPainterPathFactory* submodule
-----------------------------

The *qPainterPathFactory* submodule provides a QPainterPath_ representation of
a Glyph_'s outline.

QPainterPath_ is the Qt class for Bézier paths. It accomodates cubic or
quadratic outlines and has a pen interface.

You can then draw such paths on screen with the QPainter_ method
``drawPath()``.

.. _Glyph: http://ts-defcon.readthedocs.org/en/ufo3/objects/glyph.html
.. _QPainter: http://doc.qt.io/qt-6/qpainter.html
.. _QPainterPath: http://doc.qt.io/qt-6/qpainterpath.html
"""

from fontTools.pens.qtPen import QtPen
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath


def QPainterPathFactory(glyph):
    # Pass path= explicitly so fontTools.pens.qtPen.QtPen does not fall back
    # to its own internal Qt5-binding QPainterPath import — that fallback
    # only triggers when path is left as None, and mixing the old Qt5
    # binding's QPainterPath into a PySide6 app is exactly what caused the
    # objc framework collision / QPixmap crash during the port.
    pen = QtPen(glyph.layer, path=QPainterPath())
    glyph.draw(pen)
    pen.path.setFillRule(Qt.FillRule.WindingFill)
    return pen.path
