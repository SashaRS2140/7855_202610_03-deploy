import os
from flask import Flask
from .data.repository import Repository
from .services.session_services import SessionService
from .services.cube_services import CubeInterfaceService
from .services.timer_sevice import CountupTimer
from .presentation.web_controller import web_bp
from .presentation.api_controller import api_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

    # 1. Initialize Data Layer
    # OLD: db_path = os.path.join(os.path.dirname(__file__), 'data', 'db.json') <-- DELETE THIS

    # IMPORTANT: Ensure the class name here ('Repository' )
    # matches exactly what you defined in repository.py
    repository = Repository()

    # 2. Initialize Service Layer (Injecting Repository)
    app.session_service = SessionService(repository)
    app.hw_service = CubeInterfaceService()
    app.timer = CountupTimer()

    # 3. Register Client Layer (Blueprints)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app