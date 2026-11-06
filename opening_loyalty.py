from profile_analyzer import (
    get_opening_percentages
)


def build_opening_loyalty(
    username
):

    openings = (
        get_opening_percentages(
            username
        )
    )

    if not openings:

        return {
            "favorite_opening": None,
            "loyalty_score": 0
        }

    favorite = max(
        openings,
        key=lambda x:
        openings[x]["percent"]
    )

    loyalty_score = openings[
        favorite
    ]["percent"]

    return {
        "favorite_opening": favorite,
        "loyalty_score": loyalty_score
    }