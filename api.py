import os

from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from bot_profile_builder import build_bot_profile
from bot_profile_loader import load_bot_profile
from clone_accuracy import calculate_clone_accuracy
import data_boot  # noqa: F401
import game_session
import auth
import invites
from config import (
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    MAX_PGN_BYTES,
    MAX_PGN_FILES,
    frontend_origins,
    origin_regex,
)
from security import RateLimitMiddleware

app = FastAPI(
    title="EchoChess API",
    version="1.0.0",
)

app.add_middleware(RateLimitMiddleware)
_cors = {
    "allow_origins": frontend_origins(),
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["*"],
}
_regex = origin_regex()
if _regex:
    _cors["allow_origin_regex"] = _regex
app.add_middleware(CORSMiddleware, **_cors)


class CreateEchoRequest(BaseModel):
    platform: str = "lichess"


class NewGameRequest(BaseModel):
    username: str
    player_color: str = "white"


class MoveRequest(BaseModel):
    move: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str = ""
    invite_code: str = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class InviteCreateRequest(BaseModel):
    max_uses: int = 1
    days: int = 14
    label: str = ""


class BanRequest(BaseModel):
    username: str


def _current_user(request: Request):
    token = request.cookies.get(auth.SESSION_COOKIE)
    return auth.user_from_token(token)


def require_user(request: Request):
    user = _current_user(request)
    if user is None:
        return None
    if user.get("banned"):
        return None
    return user


def require_admin(request: Request):
    user = require_user(request)
    if user is None or user.get("role") != "admin":
        return None
    return user


def _unauthorized():
    return JSONResponse({"error": "Please log in."}, status_code=401)


def _forbidden():
    return JSONResponse({"error": "You cannot access this Echo."}, status_code=403)


def _admin_forbidden():
    return JSONResponse({"error": "Admin access required."}, status_code=403)


def _banned():
    return JSONResponse({"error": "This account has been banned."}, status_code=403)


def _owns_echo(user, echo_username: str) -> bool:
    if user is None:
        return False
    return user["username"] == echo_username.strip().lower()


def _set_session_cookie(response: Response, token: str):
    response.set_cookie(
        key=auth.SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        max_age=auth.SESSION_TTL_SECONDS,
        path="/",
    )


def secure_filename(name: str) -> str:
    name = os.path.basename(name or "")
    keep = []
    for ch in name:
        if ch.isalnum() or ch in "._-":
            keep.append(ch)
        else:
            keep.append("_")
    cleaned = "".join(keep).strip("._")
    return cleaned or "upload.pgn"


def _profile_summary(username):
    profile = load_bot_profile(username)
    if profile is None:
        return None
    return {
        "username": username,
        "personality": profile.get("personality", {}),
        "clone_accuracy": calculate_clone_accuracy(username),
    }


def _enrich_profile(profile, username):
    profile["clone_accuracy"] = calculate_clone_accuracy(username)
    pgn_folder = os.path.join("users", username, "pgns")
    pgn_count = 0
    if os.path.exists(pgn_folder):
        pgn_count = len(
            [f for f in os.listdir(pgn_folder) if f.endswith(".pgn")]
        )
    profile["pgn_count"] = pgn_count
    return profile


@app.get("/health")
def health():
    return {"app": "EchoChess", "status": "ok"}


@app.get("/")
def home():
    index = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "dist",
        "index.html",
    )
    if os.path.isfile(index):
        return FileResponse(index)
    return {"app": "EchoChess", "status": "running"}


@app.post("/auth/register")
def register(body: RegisterRequest, response: Response):
    if body.password != body.confirm_password:
        return JSONResponse({"error": "Passwords do not match."}, status_code=400)

    result = auth.register_user(
        body.username,
        body.password,
        body.invite_code,
    )
    if result.get("error"):
        return JSONResponse({"error": result["error"]}, status_code=400)

    login = auth.login_user(body.username, body.password)
    if login.get("error"):
        return JSONResponse({"error": login["error"]}, status_code=400)

    _set_session_cookie(response, login["token"])
    return {"user": login["user"]}


@app.post("/auth/login")
def login(body: LoginRequest, response: Response):
    result = auth.login_user(body.username, body.password)
    if result.get("error"):
        status = 400 if "required" in result["error"] else 401
        if "banned" in result["error"].lower():
            status = 403
        return JSONResponse({"error": result["error"]}, status_code=status)

    _set_session_cookie(response, result["token"])
    return {"user": result["user"]}


@app.post("/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(auth.SESSION_COOKIE)
    auth.logout_user(token)
    response.delete_cookie(auth.SESSION_COOKIE, path="/")
    return {"status": "logged out"}


@app.get("/auth/me")
def me(request: Request):
    user = _current_user(request)
    if user is None:
        return {"user": None}
    if user.get("banned"):
        return JSONResponse({"user": None, "error": "This account has been banned."}, status_code=403)
    return {"user": user}


@app.get("/profiles")
def list_profiles(request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    summary = _profile_summary(user["username"])
    profiles = [summary] if summary else []
    return {"profiles": profiles}


@app.get("/profile/{username}")
def get_profile(username: str, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    username = username.strip().lower()
    if not _owns_echo(user, username):
        return _forbidden()
    profile = load_bot_profile(username)
    if profile is None:
        return {"error": "profile not found"}
    return _enrich_profile(profile, username)


@app.post("/echo/create")
def create_echo(body: CreateEchoRequest, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    username = user["username"]
    pgn_folder = os.path.join("users", username, "pgns")
    os.makedirs(pgn_folder, exist_ok=True)
    pgn_count = len(
        [f for f in os.listdir(pgn_folder) if f.endswith(".pgn")]
    )
    if pgn_count == 0:
        return {
            "error": "no PGN files found",
            "message": "Upload PGN files first.",
        }
    try:
        profile = build_bot_profile(username)
    except Exception:
        return {"error": "Could not create Echo. Please try again."}
    return {
        "status": "complete",
        "username": username,
        "platform": body.platform,
        "profile": _enrich_profile(profile, username),
    }


@app.get("/echo/{username}/accuracy")
def get_clone_accuracy(username: str, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    username = username.strip().lower()
    if not _owns_echo(user, username):
        return _forbidden()
    profile = load_bot_profile(username)
    if profile is None:
        return {"error": "profile not found"}
    return {
        "username": username,
        "clone_accuracy": calculate_clone_accuracy(username),
    }


@app.post("/pgn/upload/{username}")
async def upload_pgn(
    username: str,
    request: Request,
    files: list[UploadFile] = File(...),
):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    username = username.strip().lower()
    if not _owns_echo(user, username):
        return _forbidden()
    if len(files) > MAX_PGN_FILES:
        return JSONResponse(
            {"error": f"You can upload at most {MAX_PGN_FILES} files."},
            status_code=400,
        )

    pgn_folder = os.path.join("users", username, "pgns")
    os.makedirs(pgn_folder, exist_ok=True)
    saved = []
    for file in files:
        filename = secure_filename(file.filename or "")
        if not filename.lower().endswith(".pgn"):
            continue
        content = await file.read()
        if len(content) > MAX_PGN_BYTES:
            return JSONResponse(
                {"error": "A PGN file is too large."},
                status_code=400,
            )
        dest = os.path.join(pgn_folder, filename)
        with open(dest, "wb") as out:
            out.write(content)
        saved.append(filename)
    return {"username": username, "saved": saved, "count": len(saved)}


@app.post("/game/new")
def new_game(body: NewGameRequest, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    username = body.username.strip().lower()
    if not _owns_echo(user, username):
        return _forbidden()
    profile = load_bot_profile(username)
    if profile is None:
        return {"error": "profile not found"}
    if body.player_color not in ("white", "black"):
        return {"error": "player_color must be white or black"}
    try:
        state = game_session.create_game(
            username,
            body.player_color,
            owner=user["username"],
        )
    except Exception:
        return {"error": "Could not start the game. Please try again."}

    state["profile"] = {
        "username": username,
        "personality": profile.get("personality", {}),
        "dna": profile.get("dna", {}),
        "advanced_dna": profile.get("advanced_dna", {}),
        "opening_loyalty": profile.get("opening_loyalty", {}),
        "clone_accuracy": calculate_clone_accuracy(username),
    }
    return state


def _require_game_owner(session_id: str, user):
    owner = game_session.session_owner(session_id)
    if owner is None:
        return {"error": "session not found"}
    if owner != user["username"]:
        return {"error": "You cannot access this game."}
    return None


@app.get("/game/{session_id}")
def get_game(session_id: str, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    denied = _require_game_owner(session_id, user)
    if denied:
        return denied
    state = game_session.get_game(session_id)
    if state is None:
        return {"error": "session not found"}
    return state


@app.post("/game/{session_id}/move")
def make_move(session_id: str, body: MoveRequest, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    denied = _require_game_owner(session_id, user)
    if denied:
        return denied
    return game_session.make_player_move(session_id, body.move)


@app.post("/game/{session_id}/resign")
def resign(session_id: str, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    denied = _require_game_owner(session_id, user)
    if denied:
        return denied
    return game_session.resign_game(session_id)


@app.post("/game/{session_id}/draw")
def offer_draw(session_id: str, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    denied = _require_game_owner(session_id, user)
    if denied:
        return denied
    return game_session.offer_draw(session_id)


@app.post("/game/{session_id}/undo")
def undo(session_id: str, request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    denied = _require_game_owner(session_id, user)
    if denied:
        return denied
    return game_session.undo_move(session_id)


@app.get("/games")
def list_games(request: Request):
    user = require_user(request)
    if user is None:
        return _unauthorized()
    sessions = [
        s for s in game_session.list_active_sessions()
        if game_session.session_owner(s["session_id"]) == user["username"]
    ]
    return {"sessions": sessions}


@app.get("/admin/users")
def admin_users(request: Request):
    admin = require_admin(request)
    if admin is None:
        return _admin_forbidden()
    return {"users": auth.list_users_public()}


@app.get("/admin/invites")
def admin_invites(request: Request):
    admin = require_admin(request)
    if admin is None:
        return _admin_forbidden()
    return {"invites": invites.list_invites()}


@app.post("/admin/invites")
def admin_create_invite(body: InviteCreateRequest, request: Request):
    admin = require_admin(request)
    if admin is None:
        return _admin_forbidden()
    return invites.create_invite(
        admin["username"],
        max_uses=body.max_uses,
        days=body.days,
        label=body.label,
    )


@app.post("/admin/invites/{invite_id}/revoke")
def admin_revoke_invite(invite_id: str, request: Request):
    admin = require_admin(request)
    if admin is None:
        return _admin_forbidden()
    result = invites.revoke_invite(admin["username"], invite_id)
    if result.get("error"):
        return JSONResponse(result, status_code=404)
    return result


@app.post("/admin/users/ban")
def admin_ban(body: BanRequest, request: Request):
    admin = require_admin(request)
    if admin is None:
        return _admin_forbidden()
    result = auth.set_banned(admin["username"], body.username, True)
    if result.get("error"):
        return JSONResponse(result, status_code=400)
    return result


@app.post("/admin/users/unban")
def admin_unban(body: BanRequest, request: Request):
    admin = require_admin(request)
    if admin is None:
        return _admin_forbidden()
    result = auth.set_banned(admin["username"], body.username, False)
    if result.get("error"):
        return JSONResponse(result, status_code=400)
    return result


FRONTEND_DIST = os.path.join(
    os.path.dirname(__file__),
    "frontend",
    "dist",
)

if os.path.isdir(FRONTEND_DIST):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("auth/") or full_path.startswith("admin/") or full_path.startswith("game"):
            return JSONResponse({"error": "Not found"}, status_code=404)
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
