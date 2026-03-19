import os
from flask import Blueprint


static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

dashboard_bp = Blueprint('dashboard', __name__, template_folder=templates_dir, static_folder=static_dir)

#dashboard_bp = Blueprint('dashboard', __name__)

# Import routes at the bottom to avoid circular dependencies
from . import routes