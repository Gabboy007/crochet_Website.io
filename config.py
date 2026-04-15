import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "app", "static", "uploads"),
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = as_bool(os.environ.get("FLASK_DEBUG"), default=FLASK_ENV == "development")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = as_bool(
        os.environ.get("SESSION_COOKIE_SECURE"),
        default=FLASK_ENV == "production",
    )

    PREFERRED_URL_SCHEME = os.environ.get(
        "PREFERRED_URL_SCHEME",
        "https" if FLASK_ENV == "production" else "http",
    )
    SERVER_NAME = os.environ.get("SERVER_NAME") or None
    TRUST_PROXY = as_bool(os.environ.get("TRUST_PROXY"), default=False)
