from flask import Flask
from flask_cors import CORS
from .extensions import mongo, bcrypt
from .api.auth_routes import auth_bp
from .api.user_routes import user_bp
from .core.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    bcrypt.init_app(app)
    
    CORS(app)
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')

    return app