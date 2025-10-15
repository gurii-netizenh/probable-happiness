from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    ValidationError,
    NumberRange,
)
from config import Config
from models import Log, db, User
from utils import (
    get_mood_score,
    get_tip,
    log_score,
    get_user_logs,
    export_logs,
    send_summary,
)
from datetime import datetime
from urllib.parse import urlparse as url_parse
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Ensure instance folder exists
os.makedirs("instance", exist_ok=True)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Forms (unchanged)
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email registered.")


class QuizForm(FlaskForm):
    sleep = FloatField(
        "Sleep (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)]
    )
    exercise = FloatField(
        "Exercise (0-5)", validators=[DataRequired(), NumberRange(min=0, max=5)]
    )
    connections = FloatField(
        "Connections (0-5)", validators=[DataRequired(), NumberRange(min=0, max=5)]
    )
    gratitude = FloatField(
        "Gratitude (0-5)", validators=[DataRequired(), NumberRange(min=0, max=5)]
    )
    overall = FloatField(
        "Overall (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)]
    )
    log = BooleanField("Log this for trends? (requires login)")
    submit = SubmitField("Calculate My Score!")


# Init DB route (unchanged)
@app.route("/init-db")
def init_db():
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(username="admin").first():
                admin = User(username="admin", email="admin@example.com", role="admin")
                admin.set_password("adminpass")
                db.session.add(admin)
                db.session.commit()
            flash("DB initialized successfully!")
            return redirect(url_for("landing"))
        except Exception as e:
            flash(f"DB init error: {e}")
            return redirect(url_for("landing"))


# New: Landing Page (/)
@app.route("/")
def landing():
    return render_template("landing.html", title="Welcome to HappiTrack")


# New: Dedicated Quiz Route
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    form = QuizForm()
    if form.validate_on_submit():
        score = get_mood_score(request.form)
        tip = get_tip(score)
        logged = False
        if current_user.is_authenticated and form.log.data:
            log_score(current_user.id, score)
            send_summary(current_user.email, score)
            logged = True
        elif not current_user.is_authenticated:
            flash(f"Guest Score: {score}/100 - {tip}. Login to save and track trends!")
            return render_template(
                "result.html", score=score, tip=tip, guest=True, title="Result"
            )
        return render_template(
            "result.html", score=score, tip=tip, logged=logged, title="Result"
        )
    return render_template("quiz.html", form=form, title="Daily Quiz")


# Auth Routes (tweaked redirects to landing)
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully! Welcome—start tracking your happiness.")
        return redirect(url_for("login"))  # Or direct to dashboard after auto-login
    return render_template("auth/register.html", form=form, title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next") or url_for("dashboard")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("dashboard")
            return redirect(next_page)
        flash("Invalid email or password.")
    return render_template("auth/login.html", form=form, title="Login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully. Come back anytime!")
    return redirect(url_for("landing"))


# Other Routes (unchanged, but dashboard as "home")
@app.route("/dashboard")
@login_required
def dashboard():
    recent_logs = get_user_logs(current_user.id)[-5:]
    avg = sum(l["score"] for l in recent_logs) / len(recent_logs) if recent_logs else 0
    return render_template(
        "dashboard.html",
        logs=recent_logs,
        avg=round(avg, 1),
        title="Dashboard - Your Home",
    )


@app.route("/history")
@login_required
def history():
    logs = get_user_logs(current_user.id)
    avg = sum(l["score"] for l in logs) / len(logs) if logs else 0
    return render_template(
        "history.html", logs=logs, avg=round(avg, 1), title="History"
    )


@app.route("/history/export")
@login_required
def export():
    filename = export_logs(current_user.id)
    return send_file(filename, as_attachment=True, download_name="happiness_logs.csv")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", title="Profile")


@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        flash("Access denied: Admin only.")
        return redirect(url_for("dashboard"))
    all_users = User.query.all()
    global_logs = Log.query.all()
    return render_template(
        "admin.html", users=all_users, logs=global_logs, title="Admin Panel"
    )


if __name__ == "__main__":
    app.run(debug=True)
