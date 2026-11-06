import json
import os
import secrets
from datetime import datetime, timezone

import bcrypt

from config import BASE_DIR, DATA_DIR, data_file
from store import load_json, save_json, locked, utc_now, append_audit
from invites import consume_invite

USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"
SESSION_COOKIE = "echochess_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 14

# Keep compatibility with older root users.json
_LEGACY_USERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def _users_path():
    path = data_file(USERS_FILE)
    if os.path.exists(path):
        return path
    if os.path.abspath(DATA_DIR) == os.path.abspath(BASE_DIR) and os.path.exists(_LEGACY_USERS):
        return _LEGACY_USERS
    return path


def _now():
    return datetime.now(timezone.utc).timestamp()


@locked
def _load_users():
    path = _users_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


@locked
def _save_users(users):
    path = data_file(USERS_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)
    os.replace(tmp, path)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def migrate_plaintext_passwords():
    users = _load_users()
    changed = False
    for user in users:
        user.setdefault("role", "user")
        user.setdefault("banned", False)
        if user.get("password_hash"):
            user.pop("password", None)
            continue
        plaintext = user.get("password")
        if not plaintext:
            continue
        user["password_hash"] = _hash_password(plaintext)
        user.pop("password", None)
        changed = True
    if changed or users:
        _save_users(users)


def public_user(user):
    return {
        "username": user["username"].strip().lower(),
        "role": user.get("role", "user"),
        "banned": bool(user.get("banned")),
    }


def find_user(username: str):
    if not username:
        return None
    target = username.strip().lower()
    for user in _load_users():
        if user.get("username", "").strip().lower() == target:
            return user
    return None


def register_user(username: str, password: str, code: str):
    username = (username or "").strip().lower()
    password = password or ""

    if not username:
        return {"error": "Username is required."}
    if len(username) < 3:
        return {"error": "Username must be at least 3 characters."}
    if not username.replace("_", "").isalnum():
        return {"error": "Username may only contain letters, numbers, and underscores."}
    if not password:
        return {"error": "Password is required."}
    if len(password) < 8:
        return {"error": "Password must be at least 8 characters."}
    if find_user(username):
        return {"error": "Username already exists."}

    consumed = consume_invite(code, username)
    if consumed.get("error"):
        return consumed

    users = _load_users()
    users.append({
        "username": username,
        "password_hash": _hash_password(password),
        "role": "user",
        "banned": False,
        "created_at": utc_now(),
        "invite_id": consumed.get("id"),
    })
    _save_users(users)
    return {"user": public_user({"username": username, "role": "user", "banned": False})}


def login_user(username: str, password: str):
    username = (username or "").strip().lower()
    password = password or ""

    if not username:
        return {"error": "Username is required."}
    if not password:
        return {"error": "Password is required."}

    user = find_user(username)
    if not user:
        return {"error": "Invalid username or password."}

    if user.get("banned"):
        return {"error": "This account has been banned."}

    password_hash = user.get("password_hash")
    if password_hash:
        valid = _verify_password(password, password_hash)
    else:
        plaintext = user.get("password") or ""
        valid = bool(plaintext) and secrets.compare_digest(plaintext, password)
        if valid:
            users = _load_users()
            for stored in users:
                if stored.get("username", "").strip().lower() == username:
                    stored["password_hash"] = _hash_password(password)
                    stored.pop("password", None)
            _save_users(users)

    if not valid:
        return {"error": "Invalid username or password."}

    token = secrets.token_urlsafe(32)
    sessions = load_json(SESSIONS_FILE, {})
    sessions[token] = {
        "username": user["username"].strip().lower(),
        "created_at": _now(),
    }
    save_json(SESSIONS_FILE, sessions)
    return {"token": token, "user": public_user(user)}


def logout_user(token: str):
    if not token:
        return
    sessions = load_json(SESSIONS_FILE, {})
    sessions.pop(token, None)
    save_json(SESSIONS_FILE, sessions)


def user_from_token(token: str):
    if not token:
        return None
    sessions = load_json(SESSIONS_FILE, {})
    session = sessions.get(token)
    if session is None:
        return None
    if _now() - session["created_at"] > SESSION_TTL_SECONDS:
        sessions.pop(token, None)
        save_json(SESSIONS_FILE, sessions)
        return None
    user = find_user(session["username"])
    if user is None:
        sessions.pop(token, None)
        save_json(SESSIONS_FILE, sessions)
        return None
    return public_user(user)


def list_users_public():
    rows = []
    for user in _load_users():
        rows.append({
            "username": user.get("username", "").strip().lower(),
            "role": user.get("role", "user"),
            "banned": bool(user.get("banned")),
            "created_at": user.get("created_at"),
        })
    return rows


def set_banned(actor, username, banned):
    username = (username or "").strip().lower()
    users = _load_users()
    found = None
    for user in users:
        if user.get("username", "").strip().lower() == username:
            if user.get("role") == "admin":
                return {"error": "Admin accounts cannot be banned."}
            user["banned"] = bool(banned)
            found = user
            break
    if found is None:
        return {"error": "User not found."}
    _save_users(users)
    if banned:
        sessions = load_json(SESSIONS_FILE, {})
        sessions = {
            token: session
            for token, session in sessions.items()
            if session.get("username") != username
        }
        save_json(SESSIONS_FILE, sessions)
    append_audit("user.ban" if banned else "user.unban", actor, {"username": username})
    return {"user": public_user(found)}


def create_admin(username, password):
    username = (username or "").strip().lower()
    if find_user(username):
        return {"error": "Username already exists."}
    if len(password or "") < 12:
        return {"error": "Admin password must be at least 12 characters."}
    users = _load_users()
    users.append({
        "username": username,
        "password_hash": _hash_password(password),
        "role": "admin",
        "banned": False,
        "created_at": utc_now(),
    })
    _save_users(users)
    append_audit("admin.create", "bootstrap", {"username": username})
    return {"user": public_user({"username": username, "role": "admin", "banned": False})}


migrate_plaintext_passwords()
