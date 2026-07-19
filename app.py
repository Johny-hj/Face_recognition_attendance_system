
"""
Face Recognition Attendance System — Application Factory.

Creates and configures the Flask application, registers extensions,
blueprints, CLI commands, and error handlers.

Usage:
    python app.py          # Run the development server
    flask init-db          # Create all database tables
    flask seed-admin       # Create the default admin account
"""

import os

import click
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config
from models import db
from models.admin import Admin
from models.settings import Settings


def create_app(config_name=None):
    """Application factory: build and configure the Flask app.

    Args:
        config_name: Key into the ``config`` dict ('development', 'production').
                     Falls back to the ``FLASK_ENV`` environment variable, then
                     to ``'default'``.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config.get(config_name, config['default']))

    # ── Extensions ─────────────────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    csrf = CSRFProtect()
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login callback: load an Admin by primary key."""
        return Admin.query.get(int(user_id))

    # ── Upload directory ───────────────────────────────────────────────
    upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads'))
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # ── Context Processors ─────────────────────────────────────────────
    @app.context_processor
    def inject_global_settings():
        """Make application settings available to all templates."""
        # Wrap in try-except in case DB isn't initialized yet
        try:
            theme = Settings.get('theme', 'dark')
        except Exception:
            theme = 'dark'
        return dict(current_theme=theme)

    # ── Blueprints ─────────────────────────────────────────────────────
    from routes import (
        main_bp,
        dashboard_bp,
        students_bp,
        attendance_bp,
        reports_bp,
        settings_bp,
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # ── CLI commands ───────────────────────────────────────────────────
    @app.cli.command('init-db')
    def init_db():
        """Create all database tables and seed default settings."""
        db.create_all()
        Settings.seed_defaults()
        click.echo('[SUCCESS] Database tables created and default settings seeded.')

    @app.cli.command('seed-admin')
    def seed_admin():
        """Create the default admin account if it does not already exist."""
        existing = Admin.query.filter_by(username='admin').first()
        if existing:
            click.echo('[WARNING] Admin user already exists — skipping.')
            return
        admin = Admin(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        click.echo('[SUCCESS] Default admin created (username=admin, password=admin123).')

    # ── Error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(error):
        """Render a custom 404 page."""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Render a custom 500 page."""
        return render_template('errors/500.html'), 500

    # Exempt the recognition API from CSRF (receives JSON, not forms)
    csrf.exempt('attendance.recognize')

    return app


# ── Module-level app instance (for gunicorn: ``gunicorn app:app``) ────
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
