from flask import Blueprint

api_cube_bp = Blueprint('api_cube', __name__, url_prefix='/api')

# Import routes at the bottom to avoid circular dependencies
from . import routes