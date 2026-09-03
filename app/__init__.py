import os
import logging
import cloudinary
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_babel import Babel
from config import config_by_name
from logging.handlers import SMTPHandler

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
babel = Babel()

def get_locale():
    if session.get('lang'):
        return session['lang']
    return request.accept_languages.best_match(['en', 'es']) or 'en'

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'es']
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', app.config.get('MAIL_SERVER'))
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', app.config.get('MAIL_PORT', 465)))
    app.config['MAIL_USE_TLS'] = str(os.environ.get('MAIL_USE_TLS', app.config.get('MAIL_USE_TLS', 'True'))).lower() in ['true', 'on', '1']
    app.config['MAIL_USE_SSL'] = str(os.environ.get('MAIL_USE_SSL', app.config.get('MAIL_USE_SSL', 'False'))).lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', app.config.get('MAIL_USERNAME'))
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', app.config.get('MAIL_PASSWORD'))
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME'))

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
    babel.init_app(app, locale_selector=get_locale)
    init_admin(app)

    with app.app_context():
        from app import models

    # Set up production logging via SMTPHandler
    if not app.debug:
        mail_server = app.config.get('MAIL_SERVER') or os.environ.get('MAIL_SERVER')
        
        if mail_server:
            auth = None
            mail_user = app.config.get('MAIL_USERNAME') or os.environ.get('MAIL_USERNAME')
            mail_pass = app.config.get('MAIL_PASSWORD') or os.environ.get('MAIL_PASSWORD')
            
            # Using 'or' so it fails explicitly if one credential is forgotten
            if mail_user or mail_pass:
                auth = (mail_user, mail_pass)

            secure = None
            if app.config.get('MAIL_USE_TLS') or os.environ.get('MAIL_USE_TLS'):
                secure = ()

            # Ensure ADMINS is always formatted as a valid list of recipient email strings
            admins = app.config.get('ADMINS') or os.environ.get('ADMIN_EMAIL') or []
            if isinstance(admins, str):
                admins = [email.strip() for email in admins.split(',') if email.strip()]

            if admins:
                mail_port = int(app.config.get('MAIL_PORT') or os.environ.get('MAIL_PORT') or 587)
                
                mail_handler = SMTPHandler(
                    mailhost=(mail_server, mail_port),
                    fromaddr=app.config.get('MAIL_DEFAULT_SENDER') or mail_user or 'noreply@cylcae.es',
                    toaddrs=admins,
                    subject='🚨 CYLCAE Immigration Portal: Application Crash',
                    credentials=auth,
                    secure=secure,
                    timeout=10.0
                )

                mail_handler.setLevel(logging.ERROR)

                formatter = logging.Formatter(
                    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s\n'
                    '%(pathname)s:%(lineno)d'
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
