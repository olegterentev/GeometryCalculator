import uuid
from datetime import datetime, timezone

from storage import read_json, write_json
import user_service

CANVASES_FILE = "canvases.json"


def _read_canvases() -> list[dict]:
    return read_json(CANVASES_FILE, [])


def _write_canvases(canvases: list[dict]) -> None:
    write_json(CANVASES_FILE, canvases)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_published(canvas: dict) -> bool:
    return bool(canvas.get("published", False))


def _to_summary(canvas: dict, **extra) -> dict:
    return {
        "id": canvas["id"],
        "title": canvas["title"],
        "updated_at": canvas["updated_at"],
        "published": _is_published(canvas),
        **extra,
    }


def _find_canvas(canvas_id: str) -> dict | None:
    for canvas in _read_canvases():
        if canvas["id"] == canvas_id:
            return canvas
    return None


def list_for_user(user_id: str) -> list[dict]:
    return [
        _to_summary(canvas)
        for canvas in _read_canvases()
        if canvas["user_id"] == user_id
    ]


def list_published_for_others(user_id: str) -> list[dict]:
    items: list[dict] = []

    for canvas in _read_canvases():
        if canvas["user_id"] == user_id or not _is_published(canvas):
            continue

        author = user_service.get_by_id(canvas["user_id"])
        items.append(_to_summary(
            canvas,
            author_name=author["name"] if author else "Неизвестный автор",
        ))

    return items


def create(user_id: str, title: str) -> dict:
    canvas = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title.strip() or "Новый холст",
        "history": [],
        "published": False,
        "updated_at": _now_iso(),
    }
    canvases = _read_canvases()
    canvases.append(canvas)
    _write_canvases(canvases)
    return _to_summary(canvas)


def get_for_user(user_id: str, canvas_id: str) -> dict | None:
    canvas = _find_canvas(canvas_id)
    if canvas is None or canvas["user_id"] != user_id:
        return None
    return canvas


def get_for_view(user_id: str, canvas_id: str) -> tuple[dict, bool] | None:
    canvas = _find_canvas(canvas_id)
    if canvas is None:
        return None

    if canvas["user_id"] == user_id:
        return canvas, False

    if _is_published(canvas):
        return canvas, True

    return None


def set_published(user_id: str, canvas_id: str, published: bool) -> dict | None:
    canvases = _read_canvases()

    for index, canvas in enumerate(canvases):
        if canvas["id"] != canvas_id or canvas["user_id"] != user_id:
            continue

        canvases[index] = {
            **canvas,
            "published": published,
            "updated_at": _now_iso(),
        }
        _write_canvases(canvases)
        return _to_summary(canvases[index])

    return None


def save(user_id: str, canvas_id: str, history: list) -> dict | None:
    canvases = _read_canvases()

    for index, canvas in enumerate(canvases):
        if canvas["id"] != canvas_id or canvas["user_id"] != user_id:
            continue

        canvases[index] = {
            **canvas,
            "history": history,
            "updated_at": _now_iso(),
        }
        _write_canvases(canvases)
        return _to_summary(canvases[index])

    return None


def update_title(user_id: str, canvas_id: str, title: str) -> dict | None:
    canvases = _read_canvases()
    cleaned_title = title.strip() or "Новый холст"

    for index, canvas in enumerate(canvases):
        if canvas["id"] != canvas_id or canvas["user_id"] != user_id:
            continue

        canvases[index] = {
            **canvas,
            "title": cleaned_title,
            "updated_at": _now_iso(),
        }
        _write_canvases(canvases)
        return _to_summary(canvases[index])

    return None


def delete(user_id: str, canvas_id: str) -> bool:
    canvases = _read_canvases()
    next_canvases = [
        canvas for canvas in canvases
        if not (canvas["id"] == canvas_id and canvas["user_id"] == user_id)
    ]

    if len(next_canvases) == len(canvases):
        return False

    _write_canvases(next_canvases)
    return True
