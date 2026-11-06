import os
import shutil
from datetime import datetime, timezone

from config import BASE_DIR, DATA_DIR


def run_backup():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = os.path.join(BASE_DIR, "backups", stamp)
    os.makedirs(dest, exist_ok=True)

    for name in ("users.json", "invites.json", "sessions.json", "audit.jsonl"):
        src = os.path.join(DATA_DIR, name)
        if os.path.exists(src):
            shutil.copy2(src, dest)

    for folder in ("bot_profiles", "users"):
        src = os.path.join(BASE_DIR, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dest, folder), dirs_exist_ok=True)

    return dest


if __name__ == "__main__":
    print(run_backup())
