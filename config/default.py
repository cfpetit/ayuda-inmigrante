import os

basedir = os.path.abspath(os.path.dirname(__file__))

# 1. Fetch environment DATABASE_URL (used on Render/Production)
db_url = os.environ.get('DATABASE_URL')

# 2. Fix legacy 'postgres://' protocol for SQLAlchemy 1.4+ / 2.0+ compatibility
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)


class Config:
    # Security Key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Local PostgreSQL Database URI (Fallback when DATABASE_URL is not set)
    SQLALCHEMY_DATABASE_URI = db_url or 'postgresql://inmigracion_user:your_secure_password@localhost:5432/inmigracion_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit

    # Flask-Mail / SMTP Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Error Notification Recipients
    ADMINS = os.environ.get('ADMINS', 'admin@cylcae.es')


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    # Use isolated in-memory SQLite database for test suites
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


# Dictionary map used by app factory create_app()
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
