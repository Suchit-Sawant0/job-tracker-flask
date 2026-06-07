from flask import Flask,render_template,redirect,url_for
from config import Config
from extensions import db, migrate

from models.user import User
from models.job import Job
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from extensions import db, migrate, limiter

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(job_bp, url_prefix="/api")

@app.route("/")
def home():
    return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@app.route("/jobs")
def jobs_page():
    return render_template("jobs.html")


@app.route("/add-job")
def add_job_page():
    return render_template("add_job.html")

@app.route("/edit-job/<int:job_id>")
def edit_job_page(job_id):
    return render_template("edit_job.html", job_id=job_id)

if __name__=="__main__":
    app.run(debug=True)