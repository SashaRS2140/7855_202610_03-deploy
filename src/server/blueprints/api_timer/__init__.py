from flask import Blueprint

api_timer_bp = Blueprint('api_timer', __name__, url_prefix='/api')

# Import routes at the bottom to avoid circular dependencies
from . import routes