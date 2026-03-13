import os
from flask import Blueprint

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

auth_bp = Blueprint('auth', __name__, template_folder=templates_dir, static_folder=static_dir)

#auth_bp = Blueprint('auth', __name__)

# Import routes at the bottom to avoid circular dependencies
from . import routes