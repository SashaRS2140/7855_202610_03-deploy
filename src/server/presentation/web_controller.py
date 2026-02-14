from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, Response
import os
import json
import time

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

web_bp = Blueprint('web', __name__,
                   template_folder='templates',
                   static_folder=static_dir)


def get_session_service():
    """Helper to access the service layer."""
    return current_app.session_service

def get_timer_service():
    return current_app.timer


@web_bp.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for('web.login'))

    profiles = get_session_service().get_all_profiles()
    return render_template("dashboard.html", username=session["username"], profiles=profiles)


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if get_session_service().validate_user(username, password):
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for('web.home'))

        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@web_bp.route("/new_user", methods=["POST"])
def new_user():
    username = request.form.get("username")
    password = request.form.get("password")

    svc = get_session_service()

    if not username or not password:
        return render_template(
            "signup.html",
            error="Username and password are required."
        )

    if svc.get_profile(username):
        return render_template(
            "signup.html",
            error="Username already exists."
        )

    svc.create_user(username, password)

    # Auto-login after account creation
    session["logged_in"] = True
    session["username"] = username

    return redirect(url_for("web.home"))


@web_bp.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


@web_bp.route("/delete/profile", methods=["GET","POST"])
def delete_profile():
    if not session.get("logged_in"):
        return redirect(url_for("web.login"))

    get_session_service().delete_profile(session["username"])

    return redirect(url_for("web.home"))


@web_bp.route("/delete/user", methods=["GET","POST"])
def delete_user():
    if not session.get("logged_in"):
        return redirect(url_for("web.login"))

    get_session_service().delete_user(session["username"])

    return redirect(url_for("web.login"))


@web_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('web.login'))


@web_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("logged_in"): return redirect(url_for('web.login'))

    svc = get_session_service()
    username = session["username"]

    if request.method == "POST":
        data = request.form
        error = svc.validate_profile(data)
        if error:
            # Re-render form with error and submitted data
            return render_template(
                "profile.html",
                error=error,
                profile=data
            )
        # Valid -> normalize and save
        normalized_profile = svc.normalize_profile(data)
        svc.save_profile(username, normalized_profile)
        return redirect(url_for('web.home'))
    return render_template("profile.html", profile=svc.get_profile(username))



@web_bp.route("/task/timer")
def stream_timer():
    timer = get_timer_service()

    def format_mmss(seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def event_stream():
        while True:
            remaining = timer.get_remaining()  # stored in seconds
            payload = {
                "remaining_seconds": remaining,
                "remaining_mmss": format_mmss(remaining)
            }
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")

