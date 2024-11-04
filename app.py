from flask import Flask
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_jwt_extended import JWTManager
from settings import config, APPS
from dotenv import load_dotenv
import importlib
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_super_secret_key')

    # Initialize database
    from student.models import db
    db.init_app(app)

    # Initialize JWT Manager
    JWTManager(app)

    # Initialize Flask-Migrate to enable migration commands
    Migrate(app, db)  # No need to use 'migrate' directly after this line

    # Register Blueprints from APPS list
    for app_name in APPS:
        module_name, blueprint_name = app_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        blueprint = getattr(module, blueprint_name)
        app.register_blueprint(blueprint)

    return app

# This line makes 'app' available at the module level for Gunicorn and Flask CLI
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)