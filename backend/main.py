from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from fastapi.middleware.cors import CORSMiddleware
from parser import Parser
from interpritator import Interpritator
from interpritator_v2 import InterpritatorV2
import canvas_service
import user_service


app = FastAPI()
parser = Parser()
interpritator = Interpritator()
interpritator_v2 = InterpritatorV2()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()

    return None


def _require_user(authorization: str | None) -> dict:
    user = user_service.get_user_by_token(_get_token(authorization))
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return user


class CommandRequest(BaseModel):
    command: str


class UserCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    age: int | None = None


class AuthRegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=1)
    age: int | None = None


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class CanvasCreateRequest(BaseModel):
    title: str = "Новый холст"


class HistoryEntry(BaseModel):
    id: str
    command: str


class CanvasSaveRequest(BaseModel):
    history: list[HistoryEntry]


class CanvasRenameRequest(BaseModel):
    title: str


class CanvasPublishRequest(BaseModel):
    published: bool


@app.get("/")
def root():
    return {"message": "Backend works"}


@app.get("/users")
def list_users():
    return {"users": user_service.list_all()}


@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"user": user}


@app.post("/users")
def create_user(request: UserCreateRequest):
    user, error = user_service.create(request.name, request.email, request.age)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"user": user}


@app.post("/auth/register")
def register(request: AuthRegisterRequest):
    user, token, error = user_service.register(
        request.name,
        request.email,
        request.password,
        request.age,
    )
    if error:
        return {"user": None, "token": None, "error": error}
    return {"user": user, "token": token, "error": ""}


@app.post("/auth/login")
def login(request: AuthLoginRequest):
    user, token, error = user_service.login(request.email, request.password)
    if error:
        return {"user": None, "token": None, "error": error}
    return {"user": user, "token": token, "error": ""}


@app.get("/auth/me")
def me(authorization: str | None = Header(default=None)):
    user = user_service.get_user_by_token(_get_token(authorization))
    if user is None:
        return {"user": None}
    return {"user": user}


@app.get("/canvases")
def list_canvases(authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    return {"canvases": canvas_service.list_for_user(user["id"])}


@app.get("/canvases/published")
def list_published_canvases(authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    return {"canvases": canvas_service.list_published_for_others(user["id"])}


@app.post("/canvases")
def create_canvas(
    request: CanvasCreateRequest,
    authorization: str | None = Header(default=None),
):
    user = _require_user(authorization)
    canvas = canvas_service.create(user["id"], request.title)
    return {"canvas": canvas, "error": ""}


@app.get("/canvases/{canvas_id}")
def get_canvas(canvas_id: str, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    access = canvas_service.get_for_view(user["id"], canvas_id)
    if access is None:
        raise HTTPException(status_code=404, detail="Холст не найден")

    canvas, readonly = access
    return {
        "canvas": {
            "id": canvas["id"],
            "title": canvas["title"],
            "history": canvas["history"],
            "updated_at": canvas["updated_at"],
            "published": bool(canvas.get("published", False)),
            "readonly": readonly,
        }
    }


@app.put("/canvases/{canvas_id}")
def save_canvas(
    canvas_id: str,
    request: CanvasSaveRequest,
    authorization: str | None = Header(default=None),
):
    user = _require_user(authorization)
    history = [entry.model_dump() for entry in request.history]
    canvas = canvas_service.save(user["id"], canvas_id, history)
    if canvas is None:
        raise HTTPException(status_code=404, detail="Холст не найден")
    return {"canvas": canvas, "error": ""}


@app.patch("/canvases/{canvas_id}/publish")
def publish_canvas(
    canvas_id: str,
    request: CanvasPublishRequest,
    authorization: str | None = Header(default=None),
):
    user = _require_user(authorization)
    canvas = canvas_service.set_published(user["id"], canvas_id, request.published)
    if canvas is None:
        raise HTTPException(status_code=404, detail="Холст не найден")
    return {"canvas": canvas, "error": ""}


@app.patch("/canvases/{canvas_id}")
def rename_canvas(
    canvas_id: str,
    request: CanvasRenameRequest,
    authorization: str | None = Header(default=None),
):
    user = _require_user(authorization)
    canvas = canvas_service.update_title(user["id"], canvas_id, request.title)
    if canvas is None:
        raise HTTPException(status_code=404, detail="Холст не найден")
    return {"canvas": canvas, "error": ""}


@app.delete("/canvases/{canvas_id}")
def delete_canvas(canvas_id: str, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    deleted = canvas_service.delete(user["id"], canvas_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Холст не найден")
    return {"error": ""}


@app.post("/canvases/{canvas_id}/open")
def open_canvas(canvas_id: str, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    access = canvas_service.get_for_view(user["id"], canvas_id)
    if access is None:
        raise HTTPException(status_code=404, detail="Холст не найден")

    canvas, readonly = access
    result = interpritator_v2.load_history(canvas["history"])
    if result.get("error"):
        return result

    author_name = ""
    if readonly:
        author = user_service.get_by_id(canvas["user_id"])
        author_name = author["name"] if author else ""

    return {
        **result,
        "readonly": readonly,
        "author_name": author_name,
        "canvas": {
            "id": canvas["id"],
            "title": canvas["title"],
            "updated_at": canvas["updated_at"],
            "published": bool(canvas.get("published", False)),
            "readonly": readonly,
        },
    }


@app.post("/session/reset")
def reset_session():
    return interpritator_v2.load_history([])


@app.post("/commands")
def execute_command(request: CommandRequest):
    parser.command = request.command
    result = parser.parse()
    if isinstance(result, str):
        return {
            "objects": interpritator_v2.get_all(),
            "history": interpritator_v2.get_history(),
            "error": result,
        }

    return interpritator_v2.execute(result, request.command)

