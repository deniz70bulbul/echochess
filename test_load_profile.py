from bot_profile_loader import (
    load_bot_profile
)

profile = load_bot_profile(
    "deniz"
)

print(
    profile.keys()
)