from flask import Blueprint

api_session_bp = Blueprint('api_session', __name__, url_prefix='/api')

# Import routes at the bottom to avoid circular dependencies
from . import routes