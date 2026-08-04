from flask import Flask
from app.config import Config
from app.extensions import db, bcrypt, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.booking import booking_bp
    from app.routes.passes import passes_bp
    from app.routes.payment import payment_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(passes_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Exempt API from CSRF for programmatic POST calls
    csrf.exempt(api_bp)

    with app.app_context():
        db.create_all()

    return app
