import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-fallback'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Base fallback in case DATABASE_URL is missing
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'

    UPLOAD_FOLDER = os.path.join(basedir, 'media')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Render/Neon URL prefix patch
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
