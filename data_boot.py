import os
import shutil

from config import BASE_DIR, DATA_DIR, EPHEMERAL


def _copy_tree(src, dest):
    if not os.path.exists(src):
        return
    os.makedirs(dest, exist_ok=True)
    if os.path.isfile(src):
        if not os.path.exists(dest):
            shutil.copy2(src, dest)
        return
    shutil.copytree(src, dest, dirs_exist_ok=True)


def prepare_persistent_data():
    if EPHEMERAL:
        return
    if os.path.abspath(DATA_DIR) == os.path.abspath(BASE_DIR):
        return

    for name in ("users.json", "invites.json", "sessions.json", "audit.jsonl"):
        src = os.path.join(BASE_DIR, name)
        dest = os.path.join(DATA_DIR, name)
        if os.path.isfile(src) and not os.path.exists(dest):
            shutil.copy2(src, dest)

    for folder in ("bot_profiles", "users"):
        src = os.path.join(BASE_DIR, folder)
        dest = os.path.join(DATA_DIR, folder)
        if os.path.isdir(src):
            _copy_tree(src, dest)
        link = os.path.join(BASE_DIR, folder)
        if os.path.islink(link):
            continue
        if os.path.abspath(dest) == os.path.abspath(link):
            continue
        if os.path.isdir(dest):
            if not os.path.exists(link):
                os.symlink(dest, link, target_is_directory=True)


prepare_persistent_data()
