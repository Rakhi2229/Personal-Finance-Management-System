import os

class Config:
    """
    Centralized configuration class for the Personal Financial Management System.
    Contains database paths, secret keys, upload directories, and security parameters.
    """
    # Base Directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Secret Key for sessions and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fintech-ultra-secure-secret-key-2026-antigravity'

    # Database Configuration (SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'fintech_pfm.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security & Session Settings
    REMEMBER_COOKIE_DURATION = 3600 * 24 * 7  # 7 days
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Report & File Export Storage Directory
    REPORTS_DIR = os.path.join(BASE_DIR, 'app', 'reports', 'generated')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    @staticmethod
    def init_app(app):
        """Ensure necessary runtime directories exist."""
        os.makedirs(os.path.join(Config.BASE_DIR, 'instance'), exist_ok=True)
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
