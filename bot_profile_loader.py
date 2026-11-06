import json
import os


def load_bot_profile(username):

    path = os.path.join(
        "bot_profiles",
        f"{username}.json"
    )

    if not os.path.exists(path):
        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)