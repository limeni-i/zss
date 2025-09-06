from flask import Flask
from flask_cors import CORS
from .extensions import mongo
from .core.config import Config
from .api.appointment_routes import appointment_bp
from .api.justification_routes import justification_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    mongo.init_app(app)
    
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
    
    app.register_blueprint(appointment_bp, url_prefix='/api')
    app.register_blueprint(justification_bp, url_prefix='/api')
    
    return app