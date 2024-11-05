from flask import Flask
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
from settings import config, APPS
from dotenv import load_dotenv
import importlib
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_super_secret_key')
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

    # Initialize database
    from student.models import db
    db.init_app(app)

    # Initialize JWT Manager
    jwt = JWTManager(app)

    # Connect to Redis
    redis_client = FlaskRedis(app)

    # Test Redis connection
    try:
        redis_client.ping()  # Ping Redis to test the connection
        logger.info("Connected to Redis successfully!")
    except Exception as e:
        logger.error("Failed to connect to Redis: %s", e)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        # Check if the token's unique ID (jti) is in Redis
        return redis_client.get(jti) is not None

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