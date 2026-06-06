import hashlib
import secrets
import uuid

from storage import read_json, write_json

USERS_FILE = "users.json"
_tokens: dict[str, str] = {}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _read_users() -> list[dict]:
    return read_json(USERS_FILE, [])


def _write_users(users: list[dict]) -> None:
    write_json(USERS_FILE, users)


def to_public(user: dict) -> dict:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "age": user.get("age"),
    }


def list_all() -> list[dict]:
    return [to_public(user) for user in _read_users()]


def get_by_id(user_id: str) -> dict | None:
    for user in _read_users():
        if user["id"] == user_id:
            return to_public(user)
    return None


def create(name: str, email: str, age: int | None = None, password: str | None = None) -> tuple[dict | None, str | None]:
    cleaned_name = name.strip()
    cleaned_email = email.strip().lower()

    if not cleaned_name:
        return None, "Поле name обязательно"

    if not cleaned_email:
        return None, "Поле email обязательно"

    users = _read_users()
    if any(user["email"] == cleaned_email for user in users):
        return None, "Пользователь с таким email уже существует"

    user = {
        "id": str(uuid.uuid4()),
        "name": cleaned_name,
        "email": cleaned_email,
        "age": age,
    }

    if password is not None:
        user["password_hash"] = _hash_password(password)

    users.append(user)
    _write_users(users)
    return to_public(user), None


def register(name: str, email: str, password: str, age: int | None = None) -> tuple[dict | None, str | None, str | None]:
    if not password:
        return None, None, "Пароль обязателен"

    user, error = create(name, email, age, password)
    if error:
        return None, None, error

    token = secrets.token_hex(16)
    _tokens[token] = user["id"]
    return user, token, None


def login(email: str, password: str) -> tuple[dict | None, str | None, str | None]:
    cleaned_email = email.strip().lower()
    users = _read_users()

    for user in users:
        if user["email"] != cleaned_email:
            continue

        if user.get("password_hash") != _hash_password(password):
            return None, None, "Неверный email или пароль"

        token = secrets.token_hex(16)
        _tokens[token] = user["id"]
        return to_public(user), token, None

    return None, None, "Неверный email или пароль"


def get_user_by_token(token: str | None) -> dict | None:
    if not token:
        return None

    user_id = _tokens.get(token)
    if user_id is None:
        return None

    return get_by_id(user_id)
