import argparse
import getpass
import sys

import auth


def main():
    parser = argparse.ArgumentParser(description="Create the first EchoChess admin account.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", default="")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Admin password: ")
    result = auth.create_admin(args.username, password)
    if result.get("error"):
        print(result["error"])
        sys.exit(1)
    print("Admin created:", result["user"]["username"])


if __name__ == "__main__":
    main()
