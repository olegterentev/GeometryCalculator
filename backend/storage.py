import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def read_json(filename: str, default):
    path = DATA_DIR / filename
    if not path.exists():
        return default

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(filename: str, data) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
