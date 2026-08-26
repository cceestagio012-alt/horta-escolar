import os
from datetime import timedelta

from flask import Flask


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.secret_key = os.environ["SECRET_KEY"]
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    from .api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app
