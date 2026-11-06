import json
import os

from dna_analyzer import (
    analyze_dna
)

from advanced_dna import (
    build_advanced_dna
)

from opening_book_builder import (
    build_opening_book
)

from opening_dna import (
    get_opening_dna
)

from opening_loyalty import (
    build_opening_loyalty
)

from gambit_preference import (
    analyze_gambit_preference
)

from move_signature import (
    analyze_move_signature
)

from personality_builder import (
    build_personality
)
from sacrifice_detector import (
    analyze_sacrifices
)

from endgame_personality import (
    analyze_endgame_personality
)

def build_bot_profile(
    username
):

    profile = {
     "sacrifice_profile":
     analyze_sacrifices(
        username
     ),

     "endgame_personality":
    analyze_endgame_personality(
        username
    ),
        "username":
            username,

        "dna":
            analyze_dna(
                username
            ),

        "advanced_dna":
            build_advanced_dna(
                username
            ),

        "opening_dna":
            get_opening_dna(
                username
            ),

        "opening_loyalty":
            build_opening_loyalty(
                username
            ),

        "gambit_preference":
            analyze_gambit_preference(
                username
            ),

        "move_signature":
            analyze_move_signature(
                username
            ),

        "personality":
            build_personality(
                username
            ),

        "opening_book":
            build_opening_book(
                username
            )
    }

    os.makedirs(
        "bot_profiles",
        exist_ok=True
    )

    path = os.path.join(
        "bot_profiles",
        f"{username}.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            profile,
            f,
            indent=4
        )

    return profile