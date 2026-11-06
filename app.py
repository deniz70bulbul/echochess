from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from profile_analyzer import analyze_user
import json
import os

app = Flask(__name__)
app.secret_key = "chessbotv1"

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

@app.route("/")
def home():
    if "username" in session:
        return redirect("/dashboard")


    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        for user in users:

            if (
                user["username"] == username
                and user["password"] == password
            ):
                session["username"] = username
                return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Wrong username or password"
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():


    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        users = load_users()

    for user in users:

        if user["username"] == username:

            return render_template(
                "register.html",
                error="Username already exists"
            )

        users.append({
        "username": username,
        "email": email,
        "password": password
    })

        save_users(users)

    return redirect("/login")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    pgn_folder = os.path.join(
        "users",
        username,
        "pgns"
    )

    pgn_count = 0

    if os.path.exists(pgn_folder):
        pgn_count = len([
            file
            for file in os.listdir(pgn_folder)
            if file.endswith(".pgn")
        ])

    openings = analyze_user(username)

    opening_count = len(openings)

    most_played_opening = "None"

    if openings:
        most_played_opening = max(
            openings,
            key=openings.get
        )

    return render_template(
        "dashboard.html",
        username=username,
        pgn_count=pgn_count,
        opening_count=opening_count,
        most_played_opening=most_played_opening
    )


@app.route("/upload_pgn", methods=["GET", "POST"])
def upload_pgn():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        if "pgn_file" not in request.files:
            return "No file selected"

        file = request.files["pgn_file"]

        if file.filename == "":
            return "No file selected"

        username = session["username"]

        user_folder = os.path.join(
            "users",
            username,
            "pgns"
        )

        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                user_folder,
                filename
            )
        )

        return redirect("/dashboard")

    return render_template("upload_pgn.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)