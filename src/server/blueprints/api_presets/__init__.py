from flask import Blueprint

api_presets_bp = Blueprint('api_presets', __name__, url_prefix='/api')

# Import routes at the bottom to avoid circular dependencies
from . import routes