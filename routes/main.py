"""
Main Routes.

Handles landing page, authentication (login/logout),
and simplified password reset.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.admin import Admin
from models import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    """Render the landing page. Redirect to dashboard if already logged in."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('landing.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.

    GET: Render login form.
    POST: Validate credentials and log the user in.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Please enter both username and password.', 'error')
                return render_template('auth/login.html')

            admin = Admin.query.filter_by(username=username).first()

            if admin and admin.check_password(password):
                login_user(admin)
                flash('Login successful! Welcome back.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'error')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')

    return render_template('auth/login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """Log the user out and redirect to landing page."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.landing'))


@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle simplified password reset (no email sending).

    GET: Render the forgot password form.
    POST: Look up admin by email and reset password if found.
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not email:
                flash('Please enter your email address.', 'error')
                return render_template('auth/forgot_password.html')

            if not new_password or not confirm_password:
                flash('Please enter and confirm your new password.', 'error')
                return render_template('auth/forgot_password.html')

            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('auth/forgot_password.html')

            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('auth/forgot_password.html')

            admin = Admin.query.filter_by(email=email).first()
            if admin:
                admin.set_password(new_password)
                db.session.commit()
                flash(
                    'Password has been reset successfully. You can now log in.',
                    'success'
                )
                return redirect(url_for('main.login'))
            else:
                flash('No account found with that email address.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')

    return render_template('auth/forgot_password.html')
