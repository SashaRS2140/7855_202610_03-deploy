from . import sessions_bp
from flask import render_template
from src.server.decorators.auth import login_required
from src.server.logging_config import get_logger

logger = get_logger(__name__)


@sessions_bp.route('/stats')
@login_required
def stats(uid: str):
    """Render stats page showing latest session metrics."""
    logger.info(f"Stats page loaded", extra={
        'user_id': uid,
        'endpoint': '/stats',
        'method': 'GET'
    })
    return render_template('stats.html')
