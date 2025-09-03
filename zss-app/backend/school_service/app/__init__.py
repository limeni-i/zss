from flask import Flask
from flask_cors import CORS
from .extensions import mongo
from .core.config import Config
from .api.grade_routes import grade_bp
from .api.absence_routes import absence_bp
from .api.message_routes import message_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    mongo.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
    
    app.register_blueprint(grade_bp, url_prefix='/api')
    app.register_blueprint(absence_bp, url_prefix='/api')
    app.register_blueprint(message_bp, url_prefix='/api')
    
    return app