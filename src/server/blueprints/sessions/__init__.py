from flask import Blueprint

sessions_bp = Blueprint('sessions', __name__)

# Import routes at the bottom to avoid circular dependencies
from . import routes