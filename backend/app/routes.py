from flask import Blueprint, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_db_connection
from .logger import logger

main = Blueprint("main", __name__)

PER_PAGE = 5


@main.route("/")
def home():
    return redirect("/dashboard")


# ---------------- AUTH ----------------

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return "All fields required"

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            logger.info(f"New user registered: {username}")
        except Exception:
            logger.error("User registration failed", exc_info=True)
            return "User already exists"
        finally:
            conn.close()

        return redirect("/login")

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            logger.warning(f"Failed login attempt for user: {username}")
            return "Invalid username or password"

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        logger.info(f"User logged in: {username}")
        return redirect("/dashboard")

    return render_template("login.html")


@main.route("/logout")
def logout():
    logger.info(f"User logged out: {session.get('username')}")
    session.clear()
    return redirect("/login")


# ---------------- DASHBOARD ----------------

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


# ---------------- JOBS ----------------

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
        try:
            conn.execute(
                "INSERT INTO jobs (user_id, company, status) VALUES (?, ?, ?)",
                (session["user_id"], company, status)
            )
            conn.commit()
            logger.info(
                f"Job added | user_id={session['user_id']} | company={company} | status={status}"
            )
        except Exception:
            logger.error("Failed to add job", exc_info=True)
            return "Internal server error"
        finally:
            conn.close()

        return redirect("/my-jobs")

    return render_template("add_job.html")


@main.route("/my-jobs")
def my_jobs():
    if "user_id" not in session:
        return redirect("/login")

    status = request.args.get("status")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * PER_PAGE

    conn = get_db_connection()

    query = "SELECT id, company, status FROM jobs WHERE user_id = ?"
    params = [session["user_id"]]

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND company LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([PER_PAGE, offset])

    jobs = conn.execute(query, params).fetchall()

    count_query = "SELECT COUNT(*) FROM jobs WHERE user_id = ?"
    count_params = [session["user_id"]]

    if status:
        count_query += " AND status = ?"
        count_params.append(status)

    if search:
        count_query += " AND company LIKE ?"
        count_params.append(f"%{search}%")

    total_jobs = conn.execute(count_query, count_params).fetchone()[0]
    total_pages = (total_jobs + PER_PAGE - 1) // PER_PAGE

    conn.close()

    return render_template(
        "my_jobs.html",
        jobs=jobs,
        page=page,
        total_pages=total_pages,
        status=status,
        search=search
    )


@main.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    job = conn.execute(
        "SELECT * FROM jobs WHERE id = ? AND user_id = ?",
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
        logger.info(
            f"Job updated | user_id={session['user_id']} | job_id={job_id} | status={new_status}"
        )
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

    logger.warning(
        f"Job deleted | user_id={session['user_id']} | job_id={job_id}"
    )

    return redirect("/my-jobs")
