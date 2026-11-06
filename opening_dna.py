from profile_analyzer import (
    get_opening_percentages
)


def get_opening_dna(username):

    openings = get_opening_percentages(
        username
    )

    dna = []

    for opening_name, data in openings.items():

        dna.append({
            "opening": opening_name,
            "weight": data["percent"]
        })

    dna.sort(
        key=lambda x: x["weight"],
        reverse=True
    )

    return dna