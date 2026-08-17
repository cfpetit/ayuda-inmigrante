import os
from app import create_app

env_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(env_name)

if __name__ == '__main__':
    app.run()
