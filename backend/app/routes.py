from .models import User

users = {}

from flask import Blueprint, render_template, request

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "Job Tracker Backend Running"

@main.route("/status")
def status():
    return "server is healthy"

@main.route("/add-job", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        company = request.form.get("company")
        status = request.form.get("status")

        if not company or not status:
            return "All fields are required"
        

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


    return render_template(
            "result.html",
            company=company,
            status=status
        )

    return render_template("add_job.html")
