from flask import Blueprint

presets_bp = Blueprint('presets', __name__)

# Import routes at the bottom to avoid circular dependencies
from . import routes