from geometry import *
from parser import Parser

def _index_to_label(index: int) -> str:
    parts: list[str] = []
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        parts.append(chr(65 + remainder))
    return ''.join(reversed(parts))

class Interpritator:

    def __init__(self):
        self.objects: dict[str, dict] = {}
        self.history: list[dict[str, str]] = []

    def clear(self) -> dict:
        return self._clear()

    def get_all(self) -> list[dict]:
        return list(self.objects.values())

    def get_history(self) -> list[dict[str, str]]:
        return list(self.history)

    def load_history(self, history: list) -> dict:
        validated: list[dict[str, str]] = []

        for entry in history:
            if not isinstance(entry, dict):
                return self._error("Неверный формат history")

            entry_id = entry.get("id")
            command = entry.get("command")

            if not isinstance(entry_id, str) or not isinstance(command, str):
                return self._error("Неверный формат history")

            validated.append({"id": entry_id, "command": command})

        self.history = validated
        return self._replay()

    def _clear(self) -> dict:
        self.history.clear()
        self.objects.clear()
        return self._success()

    def _error(self, message: str) -> dict:
        return {
            "objects": self.get_all(),
            "history": self.get_history(),
            "error": message,
        }

    def _success(self) -> dict:
        return {
            "objects": self.get_all(),
            "history": self.get_history(),
            "error": "",
        }

    def _upsert_history(self, entry_id: str, command: str) -> None:
        for index, entry in enumerate(self.history):
            if entry["id"] == entry_id:
                self.history[index] = {"id": entry_id, "command": command}
                return

        self.history.append({"id": entry_id, "command": command})

    def _replay(self) -> dict:
        self.objects.clear()
        parser = Parser()

        for entry in self.history:
            parser.command = entry["command"]
            parsed = parser.parse()

            if isinstance(parsed, str):
                return self._error(f'{entry["id"]}: {parsed}')

            result = self._execute_one(parsed, entry["command"])
            if result["error"]:
                return self._error(f'{entry["id"]}: {result["error"]}')

        return self._success()

    def execute(self, parsed: dict, raw_command: str) -> dict:
        operand = parsed["operand"]

        if operand == "Clear":
            return self._clear()

        if operand == "Delete":
            return self._delete(parsed)

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        snapshot = list(self.history)
        self._upsert_history(label, command)
        result = self._replay()

        if result["error"]:
            error_message = result["error"]
            self.history = snapshot
            self._replay()
            return self._error(error_message)

        return result

    def _execute_one(self, parsed: dict, raw_command: str) -> dict:
        operand = parsed["operand"]

        if operand == "Point":
            return self._point(parsed, raw_command)

        if operand == "Segment":
            return self._segment(parsed, raw_command)

        if operand == "Ray":
            return self._ray(parsed, raw_command)

        if operand == "Line":
            return self._line(parsed, raw_command)

        if operand == "Circle":
            return self._circle(parsed, raw_command)

        if operand == "Square":
            return self._square(parsed, raw_command)

        if operand == "Triangle":
            return self._triangle(parsed, raw_command)

        if operand == "Rhombus":
            return self._rhombus(parsed, raw_command)

        if operand == "Parallelogram":
            return self._parallelogram(parsed, raw_command)

        if operand == "Polygon":
            return self._polygon(parsed, raw_command)

        return self._error(f"Неизвестная операция: {operand}")

    def _refs_from_parsed(self, parsed: dict) -> set[str]:
        return {
            arg for arg in parsed.get("arg", [])
            if isinstance(arg, str)
        }

    def _collect_dependents(self, label: str) -> set[str]:
        dependents: set[str] = set()
        queue = [label]

        while queue:
            current = queue.pop()
            parser = Parser()

            for entry in self.history:
                entry_id = entry["id"]
                if entry_id == current or entry_id in dependents:
                    continue

                parser.command = entry["command"]
                parsed = parser.parse()
                if isinstance(parsed, str):
                    continue

                if current in self._refs_from_parsed(parsed):
                    dependents.add(entry_id)
                    queue.append(entry_id)

        return dependents

    def _delete(self, parsed: dict) -> dict:
        args = parsed["arg"]

        if len(args) != 1:
            return self._error("Delete требует 1 аргумент")

        label = args[0]

        if not isinstance(label, str):
            return self._error("Delete: имя объекта должно быть идентификатором")

        if not any(entry["id"] == label for entry in self.history):
            return self._error(f"Объект {label} не существует")

        to_remove = {label} | self._collect_dependents(label)
        snapshot = list(self.history)
        self.history = [entry for entry in self.history if entry["id"] not in to_remove]
        result = self._replay()

        if result["error"]:
            error_message = result["error"]
            self.history = snapshot
            self._replay()
            return self._error(error_message)

        return result

    def _point(self, parsed: dict, raw_command: str) -> dict:
        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        args = parsed['arg']
        
        if len(args) != 2:
            return self._error("Операция Point требует 2 аргумента")
        
        x, y = args

        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
             return self._error("Координаты обязанны быть числовыми значениями")

        point = Point(x, y, label)
        point.command = command

        self.objects[label] = point.get()
        return self._success()

    def resolve_point(self, label: str) -> dict | None:
        obj = self.objects.get(label)
        
        if obj is None:
            return None
        
        if obj['type'] != 'point':
            return None
        return obj

    def resolve_segment(self, label: str) -> dict | None:
        obj = self.objects.get(label)
        
        if obj is None:
            return None
        
        if obj['type'] != 'segment':
            return None
        return obj        

    def next_free_label(self, reserved: set[str] | None = None) -> str | None:
        reserved = reserved or set()
        index = 1

        while index <= 26 ** 6:
            label = _index_to_label(index)
            if label not in self.objects and label not in reserved:
                return label
            index += 1

        return None

    def _get_reserved(self, parsed: dict) -> set[str]:
        label = parsed.get('label')
        if label is not None:
            return {label}
        return set()

    def _resolve_label(self, parsed: dict, raw_command: str) -> tuple[str | None, str | None, str | None]:
        if parsed.get('label') is not None:
            return parsed['label'], raw_command, None

        label = self.next_free_label()
        if label is None:
            return None, None, 'Нет свободных имён объектов'

        op = parsed['operand']
        args = parsed['arg']
        args_str = ', '.join(str(a) for a in args)
        command = f'{label} = {op}({args_str})'

        return label, command, None

    # def find_point_at(self, x: float, y: float) -> dict | None:
    #     for obj in self.objects.values():
    #         if obj['type'] != 'point':
    #             continue
    #         if abs(obj['x'] - x) < 1e-6 and abs(obj['y'] - y) < 1e-6:
    #             return obj
    #     return None
    #
    # def ensure_point(self, x: float, y: float, reserved: set[str] | None = None) -> str | None:
    #     reserved = reserved or set()
    #     existing = self.find_point_at(x, y)
    #     if existing is not None and existing['label'] not in reserved:
    #         return existing['label']
    #     label = self.next_free_label(reserved)
    #     if label is None:
    #         return None
    #     point = Point(x, y, label)
    #     point.command = f'{label} = Point({x}, {y})'
    #     self.objects[label] = point.get()
    #     return label

    def _segment_endpoints(self, args: list):
        res = 0
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            a = self.resolve_point(args[0])
            b = self.resolve_point(args[1])
            
            if a is None:
                return (None, f'Точка {args[0]} не существует')
            
            if b is None:
                return (None, f'Точка {args[1]} не существует')

            res = ((a["x"], a["y"]), (b["x"], b["y"]))

        elif len(args) == 4:
            for i in args:
                if not isinstance(i, (int, float)):
                    return (None, f'{i} не является координатой точки')
            res = ((args[0], args[1]), (args[2], args[3]))

        elif len(args) == 3:
            if isinstance(args[0], str) and isinstance(args[1], (int, float)) and isinstance(args[2], (int, float)):
                a = self.resolve_point(args[0])

                if a is None:
                    return (None, f'Точка {args[0]} не существует')
                
                res = ((a["x"], a["y"]), (args[1], args[2]))
            
            elif isinstance(args[2], str) and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
                a = self.resolve_point(args[2])

                if a is None:
                    return (None, f'Точка {args[2]} не существует')
                
                res = ((args[0], args[1]), (a["x"], a["y"]))
            
            else:
                return (None, f'Невеные параметры команды Segment')
            
        else:
            return (None, f'Невеные параметры команды Segment')


        return res, None

    def _segment(self, parsed: dict, raw_command: str) -> dict:
        endpoints, err = self._segment_endpoints(parsed["arg"])

        if err:
            return self._error(err)
        
        (x1, y1), (x2, y2) = endpoints

        # reserved = self._get_reserved(parsed)
        # if self.ensure_point(x1, y1, reserved) is None or self.ensure_point(x2, y2, reserved) is None:
        #     return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        seg = Segment(x1, x2, y1, y2, label)
        seg.command = command
        
        self.objects[label] = seg.get()
        return self._success()

    def _line_endpoints(self, args: list):
        res = 0

        if len(args) == 1:
            a = self.resolve_segment(args[0])

            if a is None:
                return (None, f'Отрезок {args[0]} не существует')

            res = ((a['x1'], a['y1']),(a['x2'], a['y2']))


        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            a = self.resolve_point(args[0])
            b = self.resolve_point(args[1])
            
            if a is None:
                return (None, f'Точка {args[0]} не существует')
            
            if b is None:
                return (None, f'Точка {args[1]} не существует')

            res = ((a["x"], a["y"]), (b["x"], b["y"]))

        elif len(args) == 4:
            for i in args:
                if not isinstance(i, (int, float)):
                    return (None, f'{i} не является координатой точки')
            res = ((args[0], args[1]), (args[2], args[3]))

        elif len(args) == 3:
            if isinstance(args[0], str) and isinstance(args[1], (int, float)) and isinstance(args[2], (int, float)):
                a = self.resolve_point(args[0])

                if a is None:
                    return (None, f'Точка {args[0]} не существует')
                
                res = ((a["x"], a["y"]), (args[1], args[2]))
            
            elif isinstance(args[2], str) and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
                a = self.resolve_point(args[2])

                if a is None:
                    return (None, f'Точка {args[2]} не существует')
                
                res = ((args[0], args[1]), (a["x"], a["y"]))
            
            else:
                return (None, f'Невеные параметры команды Segment')

        else:
            return (None, f'Невеные параметры команды Line')

        return res, None

    def _line(self, parsed:dict, raw_command: str) -> dict:
        endpoints, err = self._line_endpoints(parsed["arg"])

        if err:
            return self._error(err)
        
        (x1, y1), (x2, y2) = endpoints

        # reserved = self._get_reserved(parsed)
        # if self.ensure_point(x1, y1, reserved) is None or self.ensure_point(x2, y2, reserved) is None:
        #     return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        line = Line(x1, y1, x2, y2, label)
        line.command = command
        
        self.objects[label] = line.get()
        return self._success()
    
    def _ray_endpoints(self, args: list):
        res = 0

        if len(args) == 1:
            a = self.resolve_segment(args[0])

            if a is None:
                return (None, f'Отрезок {args[0]} не существует')

            res = ((a['x1'], a['y1']),(a['x2'], a['y2']))


        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            a = self.resolve_point(args[0])
            b = self.resolve_point(args[1])
            
            if a is None:
                return (None, f'Точка {args[0]} не существует')
            
            if b is None:
                return (None, f'Точка {args[1]} не существует')

            res = ((a["x"], a["y"]), (b["x"], b["y"]))

        elif len(args) == 4:
            for i in args:
                if not isinstance(i, (int, float)):
                    return (None, f'{i} не является координатой точки')
            res = ((args[0], args[1]), (args[2], args[3]))

        elif len(args) == 3:
            if isinstance(args[0], str) and isinstance(args[1], (int, float)) and isinstance(args[2], (int, float)):
                a = self.resolve_point(args[0])

                if a is None:
                    return (None, f'Точка {args[0]} не существует')
                
                res = ((a["x"], a["y"]), (args[1], args[2]))
            
            elif isinstance(args[2], str) and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
                a = self.resolve_point(args[2])

                if a is None:
                    return (None, f'Точка {args[2]} не существует')
                
                res = ((args[0], args[1]), (a["x"], a["y"]))
            
            else:
                return (None, f'Невеные параметры команды Ray')

        else:
            return (None, f'Невеные параметры команды Ray')

        return res, None

    def _ray(self, parsed: dict, raw_command: str) -> dict:
        endpoints, err = self._ray_endpoints(parsed["arg"])

        if err:
            return self._error(err)
        
        (x1, y1), (x2, y2) = endpoints

        # reserved = self._get_reserved(parsed)
        # if self.ensure_point(x1, y1, reserved) is None:
        #     return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        ray = Ray(x1, x2, y1, y2, label)
        ray.command = command
        
        self.objects[label] = ray.get()
        return self._success()

    def _circle_params(self, args: list):
        # ensure = []
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            a = self.resolve_point(args[0])
            b = self.resolve_point(args[1])

            if a is None:
                return (None, f'Точка {args[0]} не существует')

            if b is None:
                return (None, f'Точка {args[1]} не существует')

            cx, cy = a["x"], a["y"]
            r = ((b["x"] - cx) ** 2 + (b["y"] - cy) ** 2) ** 0.5

        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], (int, float)):
            a = self.resolve_point(args[0])

            if a is None:
                return (None, f'Точка {args[0]} не существует')

            cx, cy = a["x"], a["y"]
            r = args[1]

        elif len(args) == 3 and all(isinstance(i, (int, float)) for i in args):
            cx, cy, r = args
            # ensure.append((cx, cy))

        elif len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], (int, float)) and isinstance(args[2], (int, float)):
            a = self.resolve_point(args[0])

            if a is None:
                return (None, f'Точка {args[0]} не существует')

            cx, cy = a["x"], a["y"]
            px, py = args[1], args[2]
            # ensure.append((px, py))
            r = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

        elif len(args) == 3 and isinstance(args[2], str) and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            b = self.resolve_point(args[2])

            if b is None:
                return (None, f'Точка {args[2]} не существует')

            cx, cy = args[0], args[1]
            # ensure.append((cx, cy))
            r = ((b["x"] - cx) ** 2 + (b["y"] - cy) ** 2) ** 0.5

        elif len(args) == 4:
            for i in args:
                if not isinstance(i, (int, float)):
                    return (None, f'{i} не является координатой точки')

            cx, cy, px, py = args
            # ensure.append((cx, cy))
            # ensure.append((px, py))
            r = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

        else:
            return (None, f'Невеные параметры команды Circle')

        if r <= 1e-9:
            return (None, f'Радиус окружности должен быть больше 0')

        return ((cx, cy, r), None)
        # return (((cx, cy, r), ensure), None)

    def _circle(self, parsed: dict, raw_command: str) -> dict:
        result, err = self._circle_params(parsed["arg"])

        if err:
            return self._error(err)

        cx, cy, r = result
        # (cx, cy, r), ensure = result

        # reserved = self._get_reserved(parsed)
        # for x, y in ensure:
        #     if self.ensure_point(x, y, reserved) is None:
        #         return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        circle = Circle(cx, cy, r, label)
        circle.command = command

        self.objects[label] = circle.get()
        return self._success()

    def _triangle_vertices(self, args: list):
        vertices = []
        i = 0

        while i < len(args) and len(vertices) < 3:
            if isinstance(args[i], str):
                point = self.resolve_point(args[i])
                if point is None:
                    return (None, f'Точка {args[i]} не существует')
                vertices.append((point["x"], point["y"]))
                i += 1
            elif (
                isinstance(args[i], (int, float))
                and i + 1 < len(args)
                and isinstance(args[i + 1], (int, float))
            ):
                vertices.append((args[i], args[i + 1]))
                i += 2
            else:
                return (None, 'Неверные параметры команды Triangle')

        if len(vertices) != 3:
            return (None, 'Triangle требует 3 точки')

        return (vertices, None)

    def _triangle(self, parsed: dict, raw_command: str) -> dict:
        vertices, err = self._triangle_vertices(parsed["arg"])

        if err:
            return self._error(err)

        (x1, y1), (x2, y2), (x3, y3) = vertices
        x1, y1 = round(x1, 2), round(y1, 2)
        x2, y2 = round(x2, 2), round(y2, 2)
        x3, y3 = round(x3, 2), round(y3, 2)

        # reserved = self._get_reserved(parsed)
        # for x, y in ((x1, y1), (x2, y2), (x3, y3)):
        #     if self.ensure_point(x, y, reserved) is None:
        #         return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        triangle = Triangle(x1, y1, x2, y2, x3, y3, label)
        triangle.command = command

        self.objects[label] = triangle.get()
        return self._success()

    def _rhombus_vertices(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        dir_x: float, dir_y: float,
    ):
        x1 = round(x1, 2)
        y1 = round(y1, 2)
        x2 = round(x2, 2)
        y2 = round(y2, 2)

        vx = x2 - x1
        vy = y2 - y1
        side = (vx ** 2 + vy ** 2) ** 0.5

        if side < 1e-9:
            return (None, 'Сторона ромба не может быть нулевой')

        dx = dir_x - x1
        dy = dir_y - y1
        direction = (dx ** 2 + dy ** 2) ** 0.5

        if direction < 1e-9:
            return (None, 'Точка направления не должна совпадать с началом стороны')

        px = dx / direction * side
        py = dy / direction * side

        x3 = round(x2 + px, 2)
        y3 = round(y2 + py, 2)
        x4 = round(x1 + px, 2)
        y4 = round(y1 + py, 2)

        # p1 → p2 — сторона, p2 → p3 → p4 → p1
        return ((x1, y1, x2, y2, x3, y3, x4, y4), None)

    def _rhombus(self, parsed: dict, raw_command: str) -> dict:
        points, err = self._triangle_vertices(parsed["arg"])

        if err:
            return self._error(err.replace('Triangle', 'Rhombus'))

        (x1, y1), (x2, y2), (dir_x, dir_y) = points

        verts, err = self._rhombus_vertices(x1, y1, x2, y2, dir_x, dir_y)

        if err:
            return self._error(err)

        rx1, ry1, rx2, ry2, rx3, ry3, rx4, ry4 = verts

        # reserved = self._get_reserved(parsed)
        # for x, y in ((rx1, ry1), (rx2, ry2), (rx3, ry3), (rx4, ry4)):
        #     if self.ensure_point(x, y, reserved) is None:
        #         return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        rhombus = Rhombus(rx1, ry1, rx2, ry2, rx3, ry3, rx4, ry4, label)
        rhombus.command = command

        self.objects[label] = rhombus.get()
        return self._success()

    def _parallelogram_vertices(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        x4: float, y4: float,
    ):
        x1 = round(x1, 2)
        y1 = round(y1, 2)
        x2 = round(x2, 2)
        y2 = round(y2, 2)
        x4 = round(x4, 2)
        y4 = round(y4, 2)

        if abs(x1 - x2) < 1e-9 and abs(y1 - y2) < 1e-9:
            return (None, 'Сторона параллелограмма не может быть нулевой')

        if abs(x1 - x4) < 1e-9 and abs(y1 - y4) < 1e-9:
            return (None, 'Смежные вершины не должны совпадать')

        px = x4 - x1
        py = y4 - y1
        x3 = round(x2 + px, 2)
        y3 = round(y2 + py, 2)

        # p1 → p2 — сторона, p2 → p3 → p4 → p1
        return ((x1, y1, x2, y2, x3, y3, x4, y4), None)

    def _parallelogram(self, parsed: dict, raw_command: str) -> dict:
        points, err = self._triangle_vertices(parsed["arg"])

        if err:
            return self._error(err.replace('Triangle', 'Parallelogram'))

        (x1, y1), (x2, y2), (x4, y4) = points

        verts, err = self._parallelogram_vertices(x1, y1, x2, y2, x4, y4)

        if err:
            return self._error(err)

        px1, py1, px2, py2, px3, py3, px4, py4 = verts

        # reserved = self._get_reserved(parsed)
        # for x, y in ((px1, py1), (px2, py2), (px3, py3), (px4, py4)):
        #     if self.ensure_point(x, y, reserved) is None:
        #         return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        parallelogram = Parallelogram(px1, py1, px2, py2, px3, py3, px4, py4, label)
        parallelogram.command = command

        self.objects[label] = parallelogram.get()
        return self._success()

    def _polygon_vertices(self, args: list):
        vertices = []
        i = 0

        while i < len(args):
            if isinstance(args[i], str):
                point = self.resolve_point(args[i])
                if point is None:
                    return (None, f'Точка {args[i]} не существует')
                vertices.append((point["x"], point["y"]))
                i += 1
            elif (
                isinstance(args[i], (int, float))
                and i + 1 < len(args)
                and isinstance(args[i + 1], (int, float))
            ):
                vertices.append((args[i], args[i + 1]))
                i += 2
            else:
                return (None, 'Неверные параметры команды Polygon')

        if len(vertices) < 3:
            return (None, 'Polygon требует минимум 3 точки')

        return ([(round(x, 2), round(y, 2)) for x, y in vertices], None)

    def _polygon(self, parsed: dict, raw_command: str) -> dict:
        vertices, err = self._polygon_vertices(parsed["arg"])

        if err:
            return self._error(err)

        # reserved = self._get_reserved(parsed)
        # for x, y in vertices:
        #     if self.ensure_point(x, y, reserved) is None:
        #         return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        polygon = Polygon(vertices, label)
        polygon.command = command

        self.objects[label] = polygon.get()
        return self._success()

    def _square_vertices(self, x1: float, y1: float, x2: float, y2: float):
        x1 = round(x1, 2)
        y1 = round(y1, 2)
        x2 = round(x2, 2)
        y2 = round(y2, 2)

        vx = x2 - x1
        vy = y2 - y1
        px = -vy
        py = vx

        x3 = round(x2 + px, 2)
        y3 = round(y2 + py, 2)
        x4 = round(x1 + px, 2)
        y4 = round(y1 + py, 2)

        # p1 → p2 — сторона, p2 → p3 → p4 → p1
        return x1, y1, x2, y2, x3, y3, x4, y4

    def _square(self, parsed: dict, raw_command: str) -> dict:
        endpoints, err = self._segment_endpoints(parsed["arg"])

        if err:
            return self._error(err)

        (x1, y1), (x2, y2) = endpoints

        if abs(x1 - x2) < 1e-9 and abs(y1 - y2) < 1e-9:
            return self._error('Точки квадрата не должны совпадать')

        verts = self._square_vertices(x1, y1, x2, y2)
        sx1, sy1, sx2, sy2, sx3, sy3, sx4, sy4 = verts

        # reserved = self._get_reserved(parsed)
        # for x, y in ((sx1, sy1), (sx2, sy2), (sx3, sy3), (sx4, sy4)):
        #     if self.ensure_point(x, y, reserved) is None:
        #         return self._error('Нет свободных имён объектов')

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        square = Square(*verts, label)
        square.command = command

        self.objects[label] = square.get()
        return self._success()
