from math import radians

from fontTools.misc.transform import Transform

ORIGIN_CENTER = 0
ORIGIN_BOTTOM_LEFT = 1
ORIGIN_ZERO = 2


def buildTransform(origin, move=(0, 0), scale=(1, 1), rotate=0, skew=0):
    """
    Scale, skew, rotate and then move, all around *origin*. Angles are in
    degrees, counter-clockwise positive as seen in the (y-up) glyph view; a
    positive skew leans the top to the right.
    """
    ox, oy = origin
    # fontTools applies the most recently chained operation first
    return (
        Transform()
        .translate(ox + move[0], oy + move[1])
        .rotate(radians(rotate))
        .skew(radians(skew), 0)
        .scale(scale[0], scale[1])
        .translate(-ox, -oy)
    )


def transformTargets(glyph):
    """
    Returns (points, anchors, components, guidelines, hadSelection). Points
    are (contour, point) pairs. With nothing selected, everything in the
    glyph except its guidelines.
    """
    points = [(c, p) for c in glyph for p in c if p.selected]
    anchors = [a for a in glyph.anchors if a.selected]
    components = [c for c in glyph.components if c.selected]
    guidelines = [g for g in glyph.guidelines if g.selected]
    if points or anchors or components or guidelines:
        return points, anchors, components, guidelines, True
    points = [(c, p) for c in glyph for p in c]
    return points, list(glyph.anchors), list(glyph.components), [], False


def targetBounds(points, anchors, components):
    xs, ys = [], []
    for _, p in points:
        xs.append(p.x)
        ys.append(p.y)
    for a in anchors:
        xs.append(a.x)
        ys.append(a.y)
    for c in components:
        b = c.bounds
        if b is not None:
            xs.extend((b[0], b[2]))
            ys.extend((b[1], b[3]))
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def applyTransform(glyph, matrix, rounding=False):
    """
    Apply *matrix* to the selected elements of *glyph* (or to the whole glyph
    if nothing is selected) as a single undo step. Returns False if there was
    nothing to transform.
    """
    if not isinstance(matrix, Transform):
        matrix = Transform(*matrix)
    points, anchors, components, guidelines, _ = transformTargets(glyph)
    if not (points or anchors or components or guidelines):
        return False

    def fix(v):
        return round(v) if rounding else v

    glyph.beginUndoGroup()
    try:
        glyph.holdNotifications()
        try:
            touched = set()
            for contour, point in points:
                x, y = matrix.transformPoint((point.x, point.y))
                point.x, point.y = fix(x), fix(y)
                touched.add(contour)
            for anchor in anchors:
                x, y = matrix.transformPoint((anchor.x, anchor.y))
                anchor.x, anchor.y = fix(x), fix(y)
            for component in components:
                new = matrix.transform(Transform(*component.transformation))
                a, b, c, d, e, f = new
                component.transformation = (a, b, c, d, fix(e), fix(f))
            for guideline in guidelines:
                guideline.transform(matrix)
            for contour in touched:
                contour.dirty = True
        finally:
            glyph.releaseHeldNotifications()
    finally:
        glyph.endUndoGroup()
    return True


def transformGlyph(glyph, originMode, move, scale, rotate, skew, rounding):
    """
    Used by the Transform dialog: like applyTransform, with the origin picked
    from the bounds of whatever is being transformed.
    """
    points, anchors, components, guidelines, _ = transformTargets(glyph)
    if not (points or anchors or components or guidelines):
        return False
    xMin, yMin, xMax, yMax = targetBounds(points, anchors, components) or (0, 0, 0, 0)
    if originMode == ORIGIN_ZERO:
        origin = (0, 0)
    elif originMode == ORIGIN_BOTTOM_LEFT:
        origin = (xMin, yMin)
    else:
        origin = ((xMin + xMax) / 2, (yMin + yMax) / 2)
    matrix = buildTransform(origin, move, scale, rotate, skew)
    return applyTransform(glyph, matrix, rounding)


def alignSelectedContours(glyph, axis, mode):
    """
    Move every contour that has a selected point so that, along *axis* ("x" or
    "y"), their minimum, center or maximum (*mode* "min", "center" or "max")
    line up. "min" is left/bottom, "max" is right/top.
    """
    isX = axis == "x"
    items = []
    for contour in glyph:
        selected = False
        lo = hi = None
        for pt in contour:
            v = pt.x if isX else pt.y
            if lo is None or v < lo:
                lo = v
            if hi is None or v > hi:
                hi = v
            if pt.selected:
                selected = True
        if selected:
            items.append((contour, lo, hi))
    if not items:
        return False
    allLo = min(lo for _, lo, _ in items)
    allHi = max(hi for _, _, hi in items)
    if mode == "min":
        target = allLo

        def key(lo, hi):
            return lo

    elif mode == "max":
        target = allHi

        def key(lo, hi):
            return hi

    else:
        target = allLo + round(0.5 * (allHi - allLo))

        def key(lo, hi):
            return lo + round(0.5 * (hi - lo))

    glyph.beginUndoGroup()
    try:
        glyph.holdNotifications()
        try:
            for contour, lo, hi in items:
                delta = target - key(lo, hi)
                if delta:
                    contour.move((delta, 0) if isX else (0, delta))
        finally:
            glyph.releaseHeldNotifications()
    finally:
        glyph.endUndoGroup()
    return True


def mirrorSelection(glyph, axis, factor):
    """
    Mirror the selection (or the whole glyph) across a line through its
    bounds along *axis*. *factor* is 0 for the min edge, 1 for the center and
    2 for the max edge, as returned by GlyphAlignmentWidget.hOrigin/vOrigin.
    """
    points, anchors, components, guidelines, _ = transformTargets(glyph)
    bounds = targetBounds(points, anchors, components)
    if bounds is None:
        return False
    xMin, yMin, xMax, yMax = bounds
    if axis == "x":
        origin = (xMin + factor * (xMax - xMin) / 2, 0)
        scale = (-1, 1)
    else:
        origin = (0, yMin + factor * (yMax - yMin) / 2)
        scale = (1, -1)
    return applyTransform(glyph, buildTransform(origin, scale=scale))


def snapSelection(glyph, base):
    """
    Round the selected points and anchors (or all of them) to multiples of
    *base*.
    """
    if not base:
        return False
    points, anchors, components, _, _ = transformTargets(glyph)
    if not (points or anchors or components):
        return False

    def fix(v):
        return round(v / base) * base

    glyph.beginUndoGroup()
    try:
        glyph.holdNotifications()
        try:
            touched = set()
            for contour, point in points:
                point.x, point.y = fix(point.x), fix(point.y)
                touched.add(contour)
            for anchor in anchors:
                anchor.x, anchor.y = fix(anchor.x), fix(anchor.y)
            for component in components:
                a, b, c, d, e, f = component.transformation
                component.transformation = (a, b, c, d, fix(e), fix(f))
            for contour in touched:
                contour.dirty = True
        finally:
            glyph.releaseHeldNotifications()
    finally:
        glyph.endUndoGroup()
    return True


# ---------------------------------------------------------------------------
# Interactive (bounding box) transformation
# ---------------------------------------------------------------------------

# handle name -> position in the bounds, as fractions of (width, height),
# y up
HANDLES = {
    "tl": (0, 1),
    "t": (0.5, 1),
    "tr": (1, 1),
    "r": (1, 0.5),
    "br": (1, 0),
    "b": (0.5, 0),
    "bl": (0, 0),
    "l": (0, 0.5),
}
CORNER_HANDLES = ("tl", "tr", "br", "bl")


def selectionBounds(glyph):
    """
    Bounds (xMin, yMin, xMax, yMax) of what a transformation would act on, or
    None.
    """
    points, anchors, components, _, _ = transformTargets(glyph)
    return targetBounds(points, anchors, components)


def handlePoint(bounds, name):
    xMin, yMin, xMax, yMax = bounds
    fx, fy = HANDLES[name]
    return (xMin + fx * (xMax - xMin), yMin + fy * (yMax - yMin))


def transformHit(bounds, pos, scale, handleRadius=7, rotateRadius=20):
    """
    What is at canvas position *pos* for a transform box over *bounds*?

    Returns ("scale", handleName), ("move", None), ("rotate", cornerName) or
    None.
    *scale* is the size of a screen pixel in canvas units.
    """
    x, y = pos
    hit = handleRadius * scale
    for name in HANDLES:
        hx, hy = handlePoint(bounds, name)
        if abs(x - hx) <= hit and abs(y - hy) <= hit:
            return ("scale", name)
    xMin, yMin, xMax, yMax = bounds
    if xMin <= x <= xMax and yMin <= y <= yMax:
        return ("move", None)
    ring = rotateRadius * scale
    for name in CORNER_HANDLES:
        hx, hy = handlePoint(bounds, name)
        if abs(x - hx) <= ring and abs(y - hy) <= ring:
            return ("rotate", name)
    return None


def scaleMatrix(bounds, name, pos, alt=False, shift=False):
    """
    Matrix for dragging handle *name* of *bounds* to canvas position *pos*.
    The opposite handle stays put, or the center with *alt*. *shift* keeps the
    proportions.
    """
    fx, fy = HANDLES[name]
    hx, hy = handlePoint(bounds, name)
    if alt:
        xMin, yMin, xMax, yMax = bounds
        ax, ay = (xMin + xMax) / 2, (yMin + yMax) / 2
    else:
        ax, ay = handlePoint(bounds, _opposite(name))
    sx = sy = 1
    if fx != 0.5 and hx != ax:
        sx = (pos[0] - ax) / (hx - ax)
    if fy != 0.5 and hy != ay:
        sy = (pos[1] - ay) / (hy - ay)
    if shift:
        if fx == 0.5:
            sx = sy
        elif fy == 0.5:
            sy = sx
        elif abs(sx - 1) >= abs(sy - 1):
            sy = sx
        else:
            sx = sy
    return buildTransform((ax, ay), scale=(sx, sy))


def _opposite(name):
    fx, fy = HANDLES[name]
    for other, (ox, oy) in HANDLES.items():
        if ox == 1 - fx and oy == 1 - fy:
            return other


def rotateMatrix(bounds, start, pos, snap=False):
    """
    Rotation about the center of *bounds*, from the angle of *start* to the
    angle of *pos*. *snap* rounds to multiples of 15 degrees.
    """
    from math import atan2, degrees

    xMin, yMin, xMax, yMax = bounds
    cx, cy = (xMin + xMax) / 2, (yMin + yMax) / 2
    angle = degrees(atan2(pos[1] - cy, pos[0] - cx) - atan2(start[1] - cy, start[0] - cx))
    if snap:
        angle = round(angle / 15) * 15
    return buildTransform((cx, cy), rotate=angle)


def moveMatrix(start, pos, constrain=False):
    dx, dy = pos[0] - start[0], pos[1] - start[1]
    if constrain:
        if abs(dx) >= abs(dy):
            dy = 0
        else:
            dx = 0
    return buildTransform((0, 0), move=(dx, dy))


class TransformSession:
    """
    Snapshot of what is being transformed, so that every step of an
    interactive transformation is computed from the original coordinates
    (nothing accumulates) and the whole drag is a single undo step.
    """

    def __init__(self, glyph):
        points, anchors, components, _, _ = transformTargets(glyph)
        self.glyph = glyph
        self.points = [(c, p, p.x, p.y) for c, p in points]
        self.anchors = [(a, a.x, a.y) for a in anchors]
        self.components = [(c, tuple(c.transformation)) for c in components]
        self.bounds = targetBounds(points, anchors, components)

    def valid(self):
        return self.bounds is not None

    def begin(self):
        self.glyph.beginUndoGroup()

    def end(self):
        self.glyph.endUndoGroup()

    def apply(self, matrix, rounding=True):
        def fix(v):
            return round(v) if rounding else v

        glyph = self.glyph
        glyph.holdNotifications()
        try:
            touched = set()
            for contour, point, x, y in self.points:
                nx, ny = matrix.transformPoint((x, y))
                point.x, point.y = fix(nx), fix(ny)
                touched.add(contour)
            for anchor, x, y in self.anchors:
                nx, ny = matrix.transformPoint((x, y))
                anchor.x, anchor.y = fix(nx), fix(ny)
            for component, original in self.components:
                a, b, c, d, e, f = matrix.transform(Transform(*original))
                component.transformation = (a, b, c, d, fix(e), fix(f))
            for contour in touched:
                contour.dirty = True
        finally:
            glyph.releaseHeldNotifications()