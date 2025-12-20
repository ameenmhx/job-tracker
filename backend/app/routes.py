from .models import User

users = {}
jobs = {}

from flask import Blueprint, render_template, request, session


main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "Job Tracker Backend Running"

@main.route("/status")
def status():
    return "server is healthy"

@main.route("/add-job", methods=["GET", "POST"])
def add_job():
    if "user" not in session:
        return "Unauthorized. Please login first."

    username = session["user"]

    if request.method == "POST":
        company = request.form.get("company")
        status = request.form.get("status")

        if not company or not status:
            return "All fields are required"

        # initialize job list for user if not exists
        if username not in jobs:
            jobs[username] = []

        jobs[username].append({
            "company": company,
            "status": status
        })

        return render_template(
            "result.html",
            company=company,
            status=status
        )

    return render_template("add_job.html")


@main.route("/my-jobs")
def my_jobs():
    if "user" not in session:
        return "Unauthorized. Please login first."

    username = session["user"]
    user_jobs = jobs.get(username, [])

    return render_template(
        "my_jobs.html",
        jobs=user_jobs
    )


        

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "All fields required"

        if username in users:
            return "User already exists"

        users[username] = User(username, password)
        return "User registered successfully"

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "All fields required"

        user = users.get(username)

        if not user or not user.check_password(password):
            return "Invalid username or password"

        # SESSION STARTS HERE
        session["user"] = username

        return f"Welcome, {username}! You are now logged in."

    return render_template("login.html")

@main.route("/logout")
def logout():
    session.pop("user", None)
    return "You have been logged out"





    return render_template(
            "result.html",
            company=company,
            status=status
        )

    return render_template("add_job.html")
