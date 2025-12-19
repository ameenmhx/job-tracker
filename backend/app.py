from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Job Tracker Backend Running"

@app.route("/status")
def status():
    return "server is healthy"

@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        company = request.form.get("company")
        status = request.form.get("status")

        if not company or not status:
            return "All fields are required"

        return f"Job added: {company} - {status}"

    return render_template("add_job.html")

if __name__ == "__main__":
    app.run(debug=True)
