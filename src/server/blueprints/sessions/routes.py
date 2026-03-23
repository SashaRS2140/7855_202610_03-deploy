from . import sessions_bp
from flask import render_template
from src.server.decorators.auth import login_required


@sessions_bp.route('/stats')
@login_required
def stats(uid: str):
    """Render stats page showing latest session metrics."""
    return render_template('stats.html')
