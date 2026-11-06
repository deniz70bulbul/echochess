def create_dna():
    aggressive = int(input("Agresiflik (0-1000): "))
    risk = int(input("Risk (0-1000): "))
    development = int(input("Gelişim Hızı (0-1000): "))
    exchange = int(input("Taş Değişim Eğilimi (0-1000): "))

    dna = {
        "aggressive": aggressive,
        "risk": risk,
        "development": development,
        "exchange": exchange
    }

    return dna


def print_dna(dna):
    print("\nBOT DNA'SI\n")
    for key, value in dna.items():
        print(key, ":", value)