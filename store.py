import json
import os
import threading
from datetime import datetime, timezone

from config import data_file

_lock = threading.RLock()
_lock_file = None
_lock_depth = 0


def _file_lock():
    global _lock_file
    path = data_file(".lock")
    _lock_file = open(path, "a+")
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(_lock_file.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX)


def _file_unlock():
    global _lock_file
    if _lock_file is None:
        return
    try:
        if os.name == "nt":
            import msvcrt
            _lock_file.seek(0)
            msvcrt.locking(_lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(_lock_file.fileno(), fcntl.LOCK_UN)
    finally:
        _lock_file.close()
        _lock_file = None


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def load_json(name, default):
    path = data_file(name)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if data is not None else default


def save_json(name, data):
    _atomic_write(data_file(name), data)


def locked(fn):
    def wrapper(*args, **kwargs):
        global _lock_depth
        with _lock:
            if _lock_depth == 0:
                _file_lock()
            _lock_depth += 1
            try:
                return fn(*args, **kwargs)
            finally:
                _lock_depth -= 1
                if _lock_depth == 0:
                    _file_unlock()
    return wrapper


def append_audit(action, actor, detail):
    path = data_file("audit.jsonl")
    row = {
        "at": utc_now(),
        "action": action,
        "actor": actor,
        "detail": detail,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
