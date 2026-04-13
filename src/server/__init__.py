from flask import Flask
from config import Config
from .services.timer_sevice import CountupTimer
import os

from src.server.logging_config import setup_logging, get_logger

# Import blueprints
from src.server.blueprints.api_cube import api_cube_bp
from src.server.blueprints.api_presets import api_presets_bp
from src.server.blueprints.api_profile import api_profile_bp
from src.server.blueprints.api_session import api_session_bp
from src.server.blueprints.api_timer import api_timer_bp
from src.server.blueprints.auth import auth_bp
from src.server.blueprints.presets import presets_bp
from src.server.blueprints.sessions import sessions_bp
from src.server.blueprints.dashboard import dashboard_bp
from src.server.blueprints.user_info import user_info_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Determine app type: 'web' for the main app (UI + API), 'api' for REST-only
    app_type = os.getenv('APP_TYPE', 'web')
    api_blueprints = (
        api_cube_bp,
        api_presets_bp,
        api_profile_bp,
        api_session_bp,
        api_timer_bp,
    )

    # Register API blueprints for both app modes when they need to be exposed.
    # In api mode we mount only the REST surface; in web mode we expose the same
    # endpoints alongside the UI so `/api/*` is reachable from the main app.
    for blueprint in api_blueprints:
        app.register_blueprint(blueprint)

    if app_type != 'api':
        # Web mode (default): register the UI routes alongside the API surface.
        app.register_blueprint(auth_bp)
        app.register_blueprint(presets_bp)
        app.register_blueprint(sessions_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(user_info_bp)

    # Initialize Timer Object
    app.timer = CountupTimer()

    return app
