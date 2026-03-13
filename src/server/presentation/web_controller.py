import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash


static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

web_bp = Blueprint('web', __name__,
                   template_folder='templates',
                   static_folder=static_dir)


##########################################################################
###                           WEB ROUTES                               ###
##########################################################################

"""
@web_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if not session.get("logged_in"): return redirect(url_for('web.login'))

    svc = get_session_service()
    username = session["username"]

    if request.method == "POST":
        data = request.form
        error = validate_profile(data)
        if error:
            # Re-render form with error and submitted data
            # If HTMX request, return ONLY the form with the error (no header/footer)
            if request.headers.get('HX-Request'):
                return render_template("partials/profile_form.html", error=error, profile=data)

            # If Standard Request
            return render_template(
                "profile.html",
                error=error,
                profile=data
            )

        # Valid -> normalize and save
        normalized_profile = normalize_profile(data)
        svc.save_profile(username, normalized_profile)

        # Success Response
        flash("You have successfully updated your profile.")

        return redirect(url_for("web.home"))
    return render_template("profile.html", profile=svc.get_profile(username))
"""

@web_bp.route("/test")
def test_cube():
    # If you want this protected, keep the login check:
    if not session.get("logged_in"):
        return redirect(url_for('auth.login'))

    return render_template("test.html")