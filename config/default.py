import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-change-in-production')

    # Get the project root directory (~/inmigracion)
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Force upload folder to ALWAYS be ~/inmigracion/media
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'media')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
