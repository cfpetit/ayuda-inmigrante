import os
from .default import Config

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI', 'postgresql://inmigracion_user:your_secure_password@localhost:5432/inmigracion_db')
    MAIL_SUPPRESS_SEND = True
