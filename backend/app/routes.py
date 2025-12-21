from .db import get_db_connection


from .models import User


from flask import Blueprint, render_template, request, session, redirect


main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "Job Tracker Backend Running"

@main.route("/status")
def status():
    return "server is healthy"

@main.route("/add-job", methods=["GET", "POST"])
def add_job():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        company = request.form.get("company", "").strip()
        status = request.form.get("status", "").strip()

        if not company:
            return "Company name cannot be empty"

        if status not in ["Applied", "Interview", "Rejected"]:
            return "Invalid status"

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO jobs (user_id, company, status) VALUES (?, ?, ?)",
            (session["user_id"], company, status)
        )
        conn.commit()
        conn.close()

        return redirect("/my-jobs")

    return render_template("add_job.html")




@main.route("/my-jobs")
def my_jobs():
    if "user_id" not in session:
        return "Unauthorized"

    status = request.args.get("status")
    search = request.args.get("search")

    conn = get_db_connection()

    query = "SELECT id, company, status FROM jobs WHERE user_id = ?"
    params = [session["user_id"]]

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND company LIKE ?"
        params.append(f"%{search}%")

    jobs = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("my_jobs.html", jobs=jobs)



@main.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    # Fetch job and ensure ownership
    job = conn.execute(
        "SELECT id, company, status FROM jobs WHERE id = ? AND user_id = ?",
        (job_id, session["user_id"])
    ).fetchone()

    if not job:
        conn.close()
        return "Job not found or not authorized"

    if request.method == "POST":
        new_status = request.form.get("status", "").strip()

        if new_status not in ["Applied", "Interview", "Rejected"]:
            conn.close()
            return "Invalid status"

        conn.execute(
            "UPDATE jobs SET status = ? WHERE id = ? AND user_id = ?",
            (new_status, job_id, session["user_id"])
        )
        conn.commit()
        conn.close()

        return redirect("/my-jobs")

    conn.close()
    return render_template("edit_job.html", job=job)


@main.route("/delete-job/<int:job_id>")
def delete_job(job_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.execute(
        "DELETE FROM jobs WHERE id = ? AND user_id = ?",
        (job_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return "Job not found or not authorized"

    return redirect("/my-jobs")






@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "All fields required"

        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
        except:
            return "User already exists"
        finally:
            conn.close()

        return "User registered successfully"

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if not user:
            return "Invalid username or password"

        from werkzeug.security import check_password_hash
        if not check_password_hash(user["password_hash"], password):
            return "Invalid username or password"

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return "Login successful"

    return render_template("login.html")

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    applied = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE user_id = ? AND status = ?",
        (session["user_id"], "Applied")
    ).fetchone()[0]

    interview = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE user_id = ? AND status = ?",
        (session["user_id"], "Interview")
    ).fetchone()[0]

    rejected = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE user_id = ? AND status = ?",
        (session["user_id"], "Rejected")
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        applied=applied,
        interview=interview,
        rejected=rejected
    )




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
