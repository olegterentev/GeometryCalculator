import math


def _round2(value: float) -> float:
    return round(value, 2)


def _distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x2 - x1, y2 - y1)


def _point_line_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    line_len = _distance(x1, y1, x2, y2)
    if line_len < 1e-9:
        return _distance(px, py, x1, y1)

    return abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / line_len


def _heron_area(a: float, b: float, c: float) -> float:
    p = (a + b + c) / 2
    value = p * (p - a) * (p - b) * (p - c)
    if value <= 0:
        return 0.0
    return math.sqrt(value)


_EPS = 1e-9


def _cross2(ox: float, oy: float, ax: float, ay: float, bx: float, by: float) -> float:
    return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)


def _dot2(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * bx + ay * by


def _points_distinct(points: list[tuple[float, float]], label: str = 'Вершины') -> str | None:
    count = len(points)

    i = 0
    while i < count:
        j = i + 1
        while j < count:
            if _distance(points[i][0], points[i][1], points[j][0], points[j][1]) < _EPS:
                return f'{label} не должны совпадать'
            j += 1
        i += 1

    return None


def _is_convex_quad(verts: list[tuple[float, float]]) -> bool:
    signs: list[bool] = []
    i = 0

    while i < 4:
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 4]
        x3, y3 = verts[(i + 2) % 4]
        cross = _cross2(x1, y1, x2, y2, x3, y3)

        if abs(cross) > _EPS:
            signs.append(cross > 0)

        i += 1

    if len(signs) < 2:
        return False

    return all(sign == signs[0] for sign in signs)


def _quad_edges(verts: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    return (
        _distance(verts[0][0], verts[0][1], verts[1][0], verts[1][1]),
        _distance(verts[1][0], verts[1][1], verts[2][0], verts[2][1]),
        _distance(verts[2][0], verts[2][1], verts[3][0], verts[3][1]),
        _distance(verts[3][0], verts[3][1], verts[0][0], verts[0][1]),
    )


def _sides_equal(*lengths: float) -> bool:
    if not lengths:
        return True

    rounded = [_round2(length) for length in lengths]
    first = rounded[0]
    i = 1

    while i < len(rounded):
        if abs(first - rounded[i]) > _EPS:
            return False
        i += 1

    return True


class Point:
    def __init__(self, x: float, y: float, label: str):
        self.x = x
        self.y = y
        self.label = label
        self.command = ''
        self.id = label

    def get(self) -> dict:
        return{
            "id": self.label,
            "type": "point",
            "label": self.label,
            "command": self.command,
            "x": self.x,
            "y": self.y,
        }

class Segment:
    def __init__(self, x1: float, x2: float, y1: float, y2: float, label: str):
        self.label = label
        self.id = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id = label
        self.command = ''

    def length(self) -> float:
        return _round2(_distance(self.x1, self.y1, self.x2, self.y2))
    
    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "segment",
            "label": self.label,
            "command": self.command,
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
            "length": self.length(),
        }

class Line:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, label: str):
        self.label = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id = label
        self.command = ''

    def get(self) -> dict:
        return{
            "id": self.label,
            "type": "line",
            "label": self.label,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "command": self.command
        }

class Ray:
    def __init__(self, x1: float, x2: float, y1: float, y2: float, label: str):
        self.label = label
        self.id = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id = label
        self.command = ''
    
    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "ray",
            "label": self.label,
            "command": self.command,
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
        }

class Circle:
    def __init__(self, cx: float, cy: float, r: float, label: str):
        self.label = label
        self.id = label
        self.cx = cx
        self.cy = cy
        self.r = r
        self.command = ''

    def area(self) -> float:
        return _round2(math.pi * self.r ** 2)

    def perimeter(self) -> float:
        return _round2(2 * math.pi * self.r)

    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "circle",
            "label": self.label,
            "command": self.command,
            "cx": self.cx,
            "cy": self.cy,
            "r": self.r,
            "area": self.area(),
            "perimeter": self.perimeter(),
        }

class Triangle:
    @staticmethod
    def check_valid_coord(
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
    ) -> str | None:
        err = _points_distinct([(x1, y1), (x2, y2), (x3, y3)], 'Вершины треугольника')
        if err:
            return err

        if abs(_cross2(x1, y1, x2, y2, x3, y3)) < _EPS:
            return 'Точки треугольника не должны лежать на одной прямой'

        a, b, c = (
            _distance(x1, y1, x2, y2),
            _distance(x2, y2, x3, y3),
            _distance(x3, y3, x1, y1),
        )

        if a < _EPS or b < _EPS or c < _EPS:
            return 'Сторона треугольника не может быть нулевой'

        return None

    def __init__(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        label: str,
    ):
        err = Triangle.check_valid_coord(x1, y1, x2, y2, x3, y3)
        if err:
            raise ValueError(err)

        self.label = label
        self.id = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.command = ''

    def _sides(self) -> tuple[float, float, float]:
        a = _distance(self.x1, self.y1, self.x2, self.y2)
        b = _distance(self.x2, self.y2, self.x3, self.y3)
        c = _distance(self.x3, self.y3, self.x1, self.y1)
        return a, b, c

    def area(self) -> float:
        a, b, c = self._sides()
        return _round2(_heron_area(a, b, c))

    def perimeter(self) -> float:
        a, b, c = self._sides()
        return _round2(a + b + c)

    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "triangle",
            "label": self.label,
            "command": self.command,
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
            "x3": self.x3, "y3": self.y3,
            "area": self.area(),
            "perimeter": self.perimeter(),
        }

class Parallelogram:
    @staticmethod
    def check_valid_coord(
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        x4: float, y4: float,
    ) -> str | None:
        verts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        err = _points_distinct(verts, 'Вершины параллелограмма')
        if err:
            return err

        ab, bc, cd, da = _quad_edges(verts)

        if ab < _EPS or bc < _EPS:
            return 'Сторона параллелограмма не может быть нулевой'

        if abs(ab - cd) > _EPS or abs(bc - da) > _EPS:
            return 'Противоположные стороны параллелограмма должны быть равны'

        # AB ∥ DC и AD ∥ BC (p1 → p2 → p3 → p4)
        ab_dc = _cross2(0.0, 0.0, x2 - x1, y2 - y1, x3 - x4, y3 - y4)
        ad_bc = _cross2(0.0, 0.0, x4 - x1, y4 - y1, x3 - x2, y3 - y2)

        if abs(ab_dc) > _EPS or abs(ad_bc) > _EPS:
            return 'Вершины не образуют параллелограмм (порядок обхода)'

        if not _is_convex_quad(verts):
            return 'Вершины параллелограмма должны обходиться по порядку'

        return None

    def __init__(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        x4: float, y4: float,
        label: str,
    ):
        err = Parallelogram.check_valid_coord(x1, y1, x2, y2, x3, y3, x4, y4)
        if err:
            raise ValueError(err)

        self.label = label
        self.id = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4
        self.command = ''

    def _base_and_height(self) -> tuple[float, float]:
        base = _distance(self.x1, self.y1, self.x2, self.y2)
        height = _point_line_distance(self.x4, self.y4, self.x1, self.y1, self.x2, self.y2)
        return base, height

    def _adjacent_sides(self) -> tuple[float, float]:
        side_a = _distance(self.x1, self.y1, self.x2, self.y2)
        side_b = _distance(self.x1, self.y1, self.x4, self.y4)
        return side_a, side_b

    def area(self) -> float:
        base, height = self._base_and_height()
        return _round2(base * height)

    def perimeter(self) -> float:
        side_a, side_b = self._adjacent_sides()
        return _round2(2 * (side_a + side_b))

    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "parallelogram",
            "label": self.label,
            "command": self.command,
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
            "x3": self.x3, "y3": self.y3,
            "x4": self.x4, "y4": self.y4,
            "area": self.area(),
            "perimeter": self.perimeter(),
        }

class Rhombus:
    @staticmethod
    def check_valid_coord(
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        x4: float, y4: float,
    ) -> str | None:
        verts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        err = _points_distinct(verts, 'Вершины ромба')
        if err:
            return err

        ab, bc, cd, da = _quad_edges(verts)

        if ab < _EPS:
            return 'Сторона ромба не может быть нулевой'

        if not _sides_equal(ab, bc, cd, da):
            return 'Все стороны ромба должны быть равны'

        if not _is_convex_quad(verts):
            return 'Вершины ромба должны обходиться по порядку'

        return None

    def __init__(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        x4: float, y4: float,
        label: str,
    ):
        err = Rhombus.check_valid_coord(x1, y1, x2, y2, x3, y3, x4, y4)
        if err:
            raise ValueError(err)

        self.label = label
        self.id = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4
        self.command = ''

    def _diagonals(self) -> tuple[float, float]:
        d1 = _distance(self.x1, self.y1, self.x3, self.y3)
        d2 = _distance(self.x2, self.y2, self.x4, self.y4)
        return d1, d2

    def _side(self) -> float:
        return _distance(self.x1, self.y1, self.x2, self.y2)

    def area(self) -> float:
        d1, d2 = self._diagonals()
        return _round2(d1 * d2 / 2)

    def perimeter(self) -> float:
        return _round2(4 * self._side())

    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "rhombus",
            "label": self.label,
            "command": self.command,
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
            "x3": self.x3, "y3": self.y3,
            "x4": self.x4, "y4": self.y4,
            "area": self.area(),
            "perimeter": self.perimeter(),
        }

class Polygon:
    def __init__(self, vertices: list[tuple[float, float]], label: str):
        self.label = label
        self.id = label
        self.vertices = vertices
        self.command = ''

    def perimeter(self) -> float:
        n = len(self.vertices)
        if n < 2:
            return 0.0

        total = 0.0
        i = 0
        while i < n:
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]
            total += _distance(x1, y1, x2, y2)
            i += 1

        return _round2(total)

    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "polygon",
            "label": self.label,
            "command": self.command,
            "vertices": [{"x": x, "y": y} for x, y in self.vertices],
            "perimeter": self.perimeter(),
        }

class Square:
    @staticmethod
    def check_valid_coord(
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        x4: float, y4: float,
    ) -> str | None:
        verts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        err = _points_distinct(verts, 'Вершины квадрата')
        if err:
            return err

        ab, bc, cd, da = _quad_edges(verts)

        if ab < _EPS:
            return 'Сторона квадрата не может быть нулевой'

        if not _sides_equal(ab, bc, cd, da):
            return 'Все стороны квадрата должны быть равны'

        if not _is_convex_quad(verts):
            return 'Вершины квадрата должны обходиться по порядку'

        # p1 → p2 → p3 → p4: прямые углы в p2, p3, p4, p1
        if abs(_dot2(x1 - x2, y1 - y2, x3 - x2, y3 - y2)) > _EPS:
            return 'Углы квадрата должны быть прямыми'

        if abs(_dot2(x2 - x3, y2 - y3, x4 - x3, y4 - y3)) > _EPS:
            return 'Углы квадрата должны быть прямыми'

        if abs(_dot2(x3 - x4, y3 - y4, x1 - x4, y1 - y4)) > _EPS:
            return 'Углы квадрата должны быть прямыми'

        if abs(_dot2(x4 - x1, y4 - y1, x2 - x1, y2 - y1)) > _EPS:
            return 'Углы квадрата должны быть прямыми'

        return None

    def __init__(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float,
        x4: float, y4: float,
        label: str,
    ):
        err = Square.check_valid_coord(x1, y1, x2, y2, x3, y3, x4, y4)
        if err:
            raise ValueError(err)

        self.label = label
        self.id = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4
        self.command = ''

    def _side(self) -> float:
        return _distance(self.x1, self.y1, self.x2, self.y2)

    def area(self) -> float:
        side = self._side()
        return _round2(side ** 2)

    def perimeter(self) -> float:
        return _round2(4 * self._side())

    def get(self) -> dict:
        return {
            "id": self.label,
            "type": "square",
            "label": self.label,
            "command": self.command,
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
            "x3": self.x3, "y3": self.y3,
            "x4": self.x4, "y4": self.y4,
            "area": self.area(),
            "perimeter": self.perimeter(),
        }
