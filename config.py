import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("ECHOCHESS_DATA_DIR", BASE_DIR)
ENV = os.environ.get("ECHOCHESS_ENV", "development")
IS_PRODUCTION = ENV == "production"
EPHEMERAL = os.environ.get("ECHOCHESS_EPHEMERAL", "false").lower() == "true"

SECRET_KEY = os.environ.get("ECHOCHESS_SECRET_KEY", "")
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")

COOKIE_SECURE = os.environ.get(
    "ECHOCHESS_COOKIE_SECURE",
    "true" if IS_PRODUCTION else "false",
).lower() == "true"
COOKIE_SAMESITE = os.environ.get(
    "ECHOCHESS_COOKIE_SAMESITE",
    "lax" if EPHEMERAL or not IS_PRODUCTION else "none",
)

MAX_PGN_FILES = int(os.environ.get("ECHOCHESS_MAX_PGN_FILES", "8"))
MAX_PGN_BYTES = int(os.environ.get("ECHOCHESS_MAX_PGN_BYTES", str(2 * 1024 * 1024)))


def frontend_origins():
    raw = os.environ.get("ECHOCHESS_FRONTEND_ORIGINS", "")
    origins = [item.strip().rstrip("/") for item in raw.split(",") if item.strip()]
    if origins:
        return origins
    if IS_PRODUCTION:
        return []
    return [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]


def origin_regex():
    return os.environ.get(
        "ECHOCHESS_ORIGIN_REGEX",
        r"https://.*\.pages\.dev" if IS_PRODUCTION or EPHEMERAL else "",
    )


def data_file(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, name)
