from flask import Blueprint

api_profile_bp = Blueprint('api_profile', __name__, url_prefix='/api')

# Import routes at the bottom to avoid circular dependencies
from . import routes