from flask import Flask


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="")

    from .api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app
