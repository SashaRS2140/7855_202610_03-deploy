import os
from flask import Flask
from .data.repository import DatabaseRepository
from .services.session_services import SessionService
from .services.cube_services import CubeInterfaceService
from .presentation.web_controller import web_bp
from .presentation.api_controller import api_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

    # 1. Initialize Data Layer
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'db.json')
    repository = DatabaseRepository(db_path)

    # 2. Initialize Service Layer (Injecting Repository)
    app.session_service = SessionService(repository)
    app.hw_service = CubeInterfaceService()

    # 3. Register Client Layer (Blueprints)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app