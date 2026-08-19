import os
import logging
import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from config import config_by_name
from logging.handlers import SMTPHandler

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration object based on environment name
    app.config.from_object(config_by_name[config_name])

    # Safely ensure local upload folder exists if specified
    if app.config.get('UPLOAD_FOLDER'):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Configure Cloudinary for media storage if environment URL exists
    if os.environ.get('CLOUDINARY_URL'):
        cloudinary.config(cloudinary_url=os.environ.get('CLOUDINARY_URL'))

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    init_admin(app)

    with app.app_context():
        from app import models

    # Set up production logging via SMTPHandler
    if not app.debug and not app.testing:
        if app.config.get('MAIL_SERVER'):
            auth = None
            mail_user = app.config.get('MAIL_USERNAME')
            mail_pass = app.config.get('MAIL_PASSWORD')
            if mail_user and mail_pass:
                auth = (mail_user, mail_pass)

            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()

            # Ensure ADMINS is always formatted as a valid list of recipient email strings
            admins = app.config.get('ADMINS') or []
            if isinstance(admins, str):
                admins = [email.strip() for email in admins.split(',') if email.strip()]

            if admins:
                mail_handler = SMTPHandler(
                    mailhost=(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT', 587)),
                    fromaddr=app.config.get('MAIL_DEFAULT_SENDER') or mail_user or 'noreply@cylcae.es',
                    toaddrs=admins,
                    subject='🚨 CYLCAE Immigration Portal: Application Crash',
                    credentials=auth,
                    secure=secure
                )

                mail_handler.setLevel(logging.ERROR)

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

def init_admin(app):
    with app.app_context():
        # Import User here inside the app context
        from app.models import User

        # Ensure database tables exist
        db.create_all()

        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@cylcae.com')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if not admin_password:
            return  # Skip if no password environment variable is set

        admin = User.query.filter_by(email=admin_email).first()

        if not admin:
            admin = User(
                email=admin_email,
                is_admin=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"--> Default admin created: {admin_email}")
        else:
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
