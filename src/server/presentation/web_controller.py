import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash


static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

web_bp = Blueprint('web', __name__,
                   template_folder='templates',
                   static_folder=static_dir)


##########################################################################
###                           WEB ROUTES                               ###
##########################################################################

# -----Below in Progress-----#


@web_bp.route("/test")
def test_cube():
    # If you want this protected, keep the login check:
    if not session.get("logged_in"):
        return redirect(url_for('auth.login'))

    return render_template("test.html")