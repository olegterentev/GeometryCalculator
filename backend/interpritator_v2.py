from geometry import *

from parser import Parser

def _is_number(value):
    return isinstance(value, (int, float))

def _next_ascii_label(objects, reserved, base_chr):
    reserved = reserved or set()
    round_num = 0

    while round_num <= 1000:
        suffix = '' if round_num == 0 else str(round_num)
        i = 0

        while i < 26:
            label = chr(base_chr + i) + suffix
            if label not in objects and label not in reserved:
                return label
            i += 1

        round_num += 1

    return None

class InterpritatorV2:

    def __init__(self):
        self.objects: dict[str, dict] = {}
        self.history: list[dict[str, str]] = []

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

    def _rollback(self, snapshot_history, snapshot_objects):
        self.history = snapshot_history
        self.objects = snapshot_objects

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
        operand = parsed['operand']

        if operand == 'Clear':
            return self._clear()

        if operand == 'Delete':
            return self._delete(parsed)

        if operand == 'Circle':
            return self._execute_circle(parsed, raw_command)

        snapshot_history = list(self.history)
        snapshot_objects = dict(self.objects)

        label, command, err = self._resolve_label(parsed, raw_command)
        if err:
            return self._error(err)

        parsed_run = dict(parsed)
        parsed_run['label'] = label

        result = self._execute_one(parsed_run, command)
        if result['error']:
            self._rollback(snapshot_history, snapshot_objects)
            return self._error(result['error'])

        if label not in self.objects:
            self._rollback(snapshot_history, snapshot_objects)
            return self._error('Не удалось построить объект')

        obj = self.objects[label]
        entries, err = self._build_history_entries(obj, operand, parsed)

        if err:
            self._rollback(snapshot_history, snapshot_objects)
            return self._error(err)

        self._rollback(snapshot_history, snapshot_objects)

        for entry_id, cmd in entries:
            self._upsert_history(entry_id, cmd)

        result = self._replay()

        if result['error']:
            self._rollback(snapshot_history, snapshot_objects)
            return self._error(result['error'])

        return result

    def _execute_circle(self, parsed, raw_command):
        snapshot_history = list(self.history)
        snapshot_objects = dict(self.objects)

        reserved = set()
        if parsed.get('label') is not None:
            reserved.add(parsed['label'])

        normalized, err = self.normalize_circle(parsed['arg'])
        if err:
            return self._error(err)

        pending_points = []
        circle_args = []

        for item in normalized:
            if isinstance(item, str):
                circle_args.append(item)
            elif isinstance(item, tuple):
                label = self.next_point_label(reserved)
                if label is None:
                    return self._error('Нет свободных имён объектов')
                reserved.add(label)
                pending_points.append((label, item[0], item[1]))
                circle_args.append(label)
            else:
                circle_args.append(item)

        if parsed.get('label') is not None:
            main_id = parsed['label']
        else:
            main_id = self.next_line_label(reserved)
            if main_id is None:
                return self._error('Нет свободных имён объектов')

        args_str = ', '.join(str(a) for a in circle_args)
        main_command = f'{main_id} = Circle({args_str})'

        entries = []
        for label, x, y in pending_points:
            entries.append((label, f'{label} = Point({x}, {y})'))
        entries.append((main_id, main_command))

        for entry_id, command in entries:
            self._upsert_history(entry_id, command)

        result = self._replay()
        if result['error']:
            self._rollback(snapshot_history, snapshot_objects)
            return self._error(result['error'])

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
        args = parsed['arg']

        if len(args) != 1:
            return self._error('Delete требует 1 аргумент')

        label = args[0]

        if not isinstance(label, str):
            return self._error('Delete: имя объекта должно быть идентификатором')

        if not any(entry['id'] == label for entry in self.history):
            return self._error(f'Объект {label} не существует')

        to_remove = {label} | self._collect_dependents(label)
        snapshot_history = list(self.history)
        snapshot_objects = dict(self.objects)
        self.history = [entry for entry in self.history if entry['id'] not in to_remove]
        result = self._replay()

        if result['error']:
            self._rollback(snapshot_history, snapshot_objects)
            return self._error(result['error'])

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

    def next_point_label(self, reserved=None):
        reserved = reserved or set()
        return _next_ascii_label(self.objects, reserved, 65)

    def next_line_label(self, reserved=None):
        reserved = reserved or set()
        return _next_ascii_label(self.objects, reserved, 97)

    def next_figure_label(self, vertex_labels, reserved=None):
        reserved = reserved or set()
        base = ''

        for label in vertex_labels:
            base += label

        if base == '':
            return None

        if not self._name_taken(base, reserved):
            return base

        suffix = 1

        while suffix <= 1000:
            candidate = base + str(suffix)
            if not self._name_taken(candidate, reserved):
                return candidate
            suffix += 1

        return None

    def _object_exists(self, label):
        return label in self.objects

    def _name_taken(self, label, reserved=None):
        reserved = reserved or set()

        if label in self.objects or label in reserved:
            return True

        return any(entry['id'] == label for entry in self.history)

    def _resolve_label(self, parsed, raw_command):
        label = parsed.get('label')
        if label is not None:
            return label, raw_command, None

        op = parsed['operand']

        if op == 'Point':
            label = self.next_point_label()
        elif op in ('Square', 'Triangle', 'Rhombus', 'Parallelogram', 'Polygon'):
            label = self.next_line_label()
        else:
            label = self.next_line_label()

        if label is None:
            return None, None, 'Нет свободных имён объектов'

        args_str = ', '.join(str(a) for a in parsed['arg'])
        command = f'{label} = {op}({args_str})'

        return label, command, None

    def normalize_points(self, args, operand='Команда'):
        result = []
        index = 0

        while index < len(args):
            token = args[index]

            if isinstance(token, str):
                if not self._object_exists(token):
                    return None, f'Объект {token} не существует'
                result.append(token)
                index += 1
                continue

            if _is_number(token):
                if index + 1 >= len(args) or not _is_number(args[index + 1]):
                    return None, f'{operand}: ожидалась вторая координата'
                result.append((float(token), float(args[index + 1])))
                index += 2
                continue

            return None, f'{operand}: неверный аргумент {token}'

        return result, None

    def normalize_circle(self, args):
        result = []
        index = 0
        operand = 'Circle'

        while index < len(args):
            token = args[index]

            if isinstance(token, str):
                if not self._object_exists(token):
                    return None, f'Объект {token} не существует'
                result.append(token)
                index += 1
                continue

            if _is_number(token):
                if index + 1 < len(args) and _is_number(args[index + 1]):
                    result.append((float(token), float(args[index + 1])))
                    index += 2
                else:
                    result.append(float(token))
                    index += 1
                continue

            return None, f'{operand}: неверный аргумент {token}'

        return result, None

    def _is_quad_args(self, args: list) -> bool:
        if len(args) == 4 and all(isinstance(a, str) for a in args):
            return True

        if len(args) == 8 and all(_is_number(a) for a in args):
            return True

        return False

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

    def _quad_vertices(self, args: list, operand: str):
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
                vertices.append((float(args[i]), float(args[i + 1])))
                i += 2
            else:
                return (None, f'Неверные параметры команды {operand}')

        if len(vertices) != 4:
            return (None, f'{operand} требует 4 точки')

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

        try:
            triangle = Triangle(x1, y1, x2, y2, x3, y3, label)
        except ValueError as e:
            return self._error(str(e))

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
        args = parsed["arg"]

        if self._is_quad_args(args):
            points, err = self._quad_vertices(args, 'Rhombus')

            if err:
                return self._error(err)

            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = points
            x1, y1 = round(x1, 2), round(y1, 2)
            x2, y2 = round(x2, 2), round(y2, 2)
            x3, y3 = round(x3, 2), round(y3, 2)
            x4, y4 = round(x4, 2), round(y4, 2)
            rx1, ry1, rx2, ry2, rx3, ry3, rx4, ry4 = x1, y1, x2, y2, x3, y3, x4, y4
        else:
            points, err = self._triangle_vertices(args)

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

        try:
            rhombus = Rhombus(rx1, ry1, rx2, ry2, rx3, ry3, rx4, ry4, label)
        except ValueError as e:
            return self._error(str(e))

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
        args = parsed["arg"]

        if self._is_quad_args(args):
            points, err = self._quad_vertices(args, 'Parallelogram')

            if err:
                return self._error(err)

            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = points
            x1, y1 = round(x1, 2), round(y1, 2)
            x2, y2 = round(x2, 2), round(y2, 2)
            x3, y3 = round(x3, 2), round(y3, 2)
            x4, y4 = round(x4, 2), round(y4, 2)
            px1, py1, px2, py2, px3, py3, px4, py4 = x1, y1, x2, y2, x3, y3, x4, y4
        else:
            points, err = self._triangle_vertices(args)

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

        try:
            parallelogram = Parallelogram(px1, py1, px2, py2, px3, py3, px4, py4, label)
        except ValueError as e:
            return self._error(str(e))

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
        args = parsed["arg"]

        if self._is_quad_args(args):
            points, err = self._quad_vertices(args, 'Square')

            if err:
                return self._error(err)

            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = points
            sx1, sy1 = round(x1, 2), round(y1, 2)
            sx2, sy2 = round(x2, 2), round(y2, 2)
            sx3, sy3 = round(x3, 2), round(y3, 2)
            sx4, sy4 = round(x4, 2), round(y4, 2)
        else:
            endpoints, err = self._segment_endpoints(args)

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

        try:
            square = Square(sx1, sy1, sx2, sy2, sx3, sy3, sx4, sy4, label)
        except ValueError as e:
            return self._error(str(e))

        square.command = command

        self.objects[label] = square.get()
        return self._success()

    def _find_point_at(self, x: float, y: float) -> str | None:
        for obj in self.objects.values():
            if obj.get('type') != 'point':
                continue

            if abs(obj['x'] - x) < 1e-6 and abs(obj['y'] - y) < 1e-6:
                return obj['label']

        return None

    def _corners_from_object(self, obj: dict) -> list[tuple[float, float]] | None:
        kind = obj.get('type')

        if kind == 'point':
            return [(obj['x'], obj['y'])]

        if kind in ('segment', 'line', 'ray'):
            return [(obj['x1'], obj['y1']), (obj['x2'], obj['y2'])]

        if kind == 'triangle':
            return [
                (obj['x1'], obj['y1']),
                (obj['x2'], obj['y2']),
                (obj['x3'], obj['y3']),
            ]

        if kind in ('square', 'rhombus', 'parallelogram'):
            return [
                (obj['x1'], obj['y1']),
                (obj['x2'], obj['y2']),
                (obj['x3'], obj['y3']),
                (obj['x4'], obj['y4']),
            ]

        if kind == 'polygon':
            return [(v['x'], v['y']) for v in obj['vertices']]

        return None

    def _append_point_entry(
        self,
        x: float,
        y: float,
        reserved: set[str],
        entries: list[tuple[str, str]],
        ):
        label = self._find_point_at(x, y)

        if label is not None:
            return label, None

        label = self.next_point_label(reserved)

        if label is None:
            return None, 'Нет свободных имён объектов'

        reserved.add(label)
        x = round(float(x), 2)
        y = round(float(y), 2)
        entries.append((label, f'{label} = Point({x}, {y})'))

        return label, None

    def _build_history_entries(self, obj: dict, operand: str, parsed: dict) -> tuple[list[tuple[str, str]] | None, str | None]:
        corners = self._corners_from_object(obj)

        if corners is None:
            return None, f'Операция пока не реализована: {operand}'

        reserved = set()

        for entry in self.history:
            reserved.add(entry['id'])

        if parsed.get('label') is not None:
            reserved.add(parsed['label'])

        entries: list[tuple[str, str]] = []

        if operand == 'Point':
            x, y = round(corners[0][0], 2), round(corners[0][1], 2)
            label = parsed.get('label')

            if label is None:
                label = self.next_point_label(reserved)

            if label is None:
                return None, 'Нет свободных имён объектов'

            reserved.add(label)
            entries.append((label, f'{label} = Point({x}, {y})'))
            return entries, None

        point_labels: list[str] = []
        i = 0

        while i < len(corners):
            x, y = corners[i]
            label, err = self._append_point_entry(x, y, reserved, entries)

            if err:
                return None, err

            point_labels.append(label)
            i += 1

        if operand in ('Triangle', 'Square', 'Rhombus', 'Parallelogram', 'Polygon'):
            count = len(point_labels)
            j = 0

            while j < count:
                p1 = point_labels[j]
                p2 = point_labels[(j + 1) % count]
                seg_id = self.next_line_label(reserved)

                if seg_id is None:
                    return None, 'Нет свободных имён объектов'

                reserved.add(seg_id)
                entries.append((seg_id, f'{seg_id} = Segment({p1}, {p2})'))
                j += 1

        if parsed.get('label') is not None:
            figure_id = parsed['label']
        else:
            figure_id = self.next_figure_label(point_labels, reserved)

            if operand in ('Segment', 'Line', 'Ray') and figure_id is None:
                figure_id = self.next_line_label(reserved)

        if figure_id is None:
            return None, 'Нет свободных имён объектов'

        reserved.add(figure_id)
        args_str = ', '.join(point_labels)
        entries.append((figure_id, f'{figure_id} = {operand}({args_str})'))

        return entries, None
