from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    CORS(app)

    Swagger(app)  # <--- ADD THIS LINE

    from app.routes.ocr_routes import ocr_bp
    from app.routes.audio_routes import audio_bp

    app.register_blueprint(ocr_bp, url_prefix="/")
    app.register_blueprint(audio_bp, url_prefix="/")

    return app