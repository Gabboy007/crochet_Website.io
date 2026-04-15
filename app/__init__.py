import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    if app.config.get("TRUST_PROXY"):
        # Respect X-Forwarded headers when behind a reverse proxy.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models
    from app.routes import main

    app.register_blueprint(main)

    return app
