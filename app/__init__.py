import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration object based on environment name
    app.config.from_object(config_by_name[config_name])

    # Ensure the media upload folder exists on startup
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    with app.app_context():
        from app import models

    if not app.debug and not app.testing:
        if app.config.get['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=[app.config['ADMIN_EMAIL']],
                subject='🚨 Immigration Portal: Application Crash',
                credentials=auth,
                secure=secure
            )

            # Only trigger on ERROR level and above
            mail_handler.setLevel(logging.ERROR)

            # Format the email body to show the time, file, and exact error message
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            )
            mail_handler.setFormatter(formatter)

            app.logger.addHandler(mail_handler)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # Register Blueprints
    from app.public.routes import public_bp
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
