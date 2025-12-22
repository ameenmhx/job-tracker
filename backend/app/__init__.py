import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Secret key from environment variable
    app.secret_key = os.getenv("SECRET_KEY")

    # Session security settings
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax"
    )

    from .routes import main
    app.register_blueprint(main)

    return app
