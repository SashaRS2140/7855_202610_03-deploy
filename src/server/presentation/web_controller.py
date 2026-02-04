from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import os


static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

web_bp = Blueprint('web', __name__,
                   template_folder='templates',
                   static_folder=static_dir)

def get_session_service():
    """Helper to access the service layer."""
    return current_app.session_service


@web_bp.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for('web.login'))

    profiles = get_session_service().get_dashboard_data()
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

# src/server/presentation/web_controller.py

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
        result = svc.update_user_profile(username, request.form)
        if "error" in result:
            return render_template("profile.html", error=result["error"], profile=request.form)
        return redirect(url_for('web.home'))

    return render_template("profile.html", profile=svc.get_user_profile(username))