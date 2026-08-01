import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """
    Application Factory pattern for initializing the Flask FinTech application.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions with app instance
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader callback for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Custom Jinja Filters for FinTech Formatting
    @app.template_filter('currency')
    def currency_format(value):
        """Format number as INR Currency (e.g. ₹1,25,000.00)."""
        try:
            val = float(value or 0)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @app.template_filter('percentage')
    def percentage_format(value):
        """Format decimal as percentage (e.g. 24.5%)."""
        try:
            val = float(value or 0)
            return f"{val:.1f}%"
        except (ValueError, TypeError):
            return "0.0%"

    # Inject Notifications Globally into Jinja Templates
    @app.context_processor
    def inject_user_notifications():
        from flask_login import current_user
        from app.models.notification import Notification
        if current_user.is_authenticated:
            try:
                notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
                unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
                return dict(notifications=notifs, unread_count=unread)
            except Exception:
                return dict(notifications=[], unread_count=0)
        return dict(notifications=[], unread_count=0)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.income import income_bp
    from app.routes.expense import expense_bp
    from app.routes.budget import budget_bp
    from app.routes.investment import investment_bp
    from app.routes.goal import goal_bp
    from app.routes.ai import ai_bp
    from app.routes.reports import reports_bp
    from app.routes.bonus import bonus_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp, url_prefix='/income')
    app.register_blueprint(expense_bp, url_prefix='/expense')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(investment_bp, url_prefix='/investment')
    app.register_blueprint(goal_bp, url_prefix='/goal')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(bonus_bp, url_prefix='/bonus')

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Ensure tables are created on app context startup
    with app.app_context():
        db.create_all()

    return app
