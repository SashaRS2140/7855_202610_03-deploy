from flask import Blueprint

user_info_bp = Blueprint('user_info', __name__)

# Import routes at the bottom to avoid circular dependencies
from . import routes