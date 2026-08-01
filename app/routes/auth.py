from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.notification import Notification

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration with input validation and default notifications."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        risk_tolerance = request.form.get('risk_tolerance', 'Moderate')

        # Validation
        if not username or not email or not password or not full_name:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please login.', 'warning')
            return render_template('auth/register.html')

        # Create New User
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            risk_tolerance=risk_tolerance
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Add Welcome Notification
        welcome_notif = Notification(
            user_id=new_user.id,
            title='Welcome to PFM FinTech Platform! 🎉',
            message='Your account has been successfully created. Start by adding your income and expenses to unlock AI Insights.',
            type='success'
        )
        db.session.add(welcome_notif)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email_or_username = request.form.get('email_or_username', '').strip()
        password = request.form.get('password', '').strip()
        remember = True if request.form.get('remember') else False

        if not email_or_username or not password:
            flash('Please enter both username/email and password.', 'danger')
            return render_template('auth/login.html')

        # Case-insensitive lookup for both username and email
        user = User.query.filter(
            (User.email.ilike(email_or_username)) | (User.username.ilike(email_or_username))
        ).first()

        if not user or not user.check_password(password):
            flash('Invalid username/email or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logs out current user."""
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management and preferences update."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        risk_tolerance = request.form.get('risk_tolerance', 'Moderate')
        currency = request.form.get('currency', 'INR')
        monthly_target_savings = float(request.form.get('monthly_target_savings', 0.0) or 0.0)

        if not full_name:
            flash('Full name cannot be empty.', 'danger')
            return render_template('auth/profile.html')

        current_user.full_name = full_name
        current_user.risk_tolerance = risk_tolerance
        current_user.currency = currency
        current_user.monthly_target_savings = monthly_target_savings
        db.session.commit()

        flash('Profile settings updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Security password update route."""
    current_pass = request.form.get('current_password', '')
    new_pass = request.form.get('new_password', '')
    confirm_pass = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pass):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('auth.profile'))

    if len(new_pass) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('auth.profile'))

    if new_pass != confirm_pass:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.profile'))

    current_user.set_password(new_pass)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/reset-data', methods=['POST'])
@login_required
def reset_data():
    """Wipes all pre-filled/demo financial data (expenses, incomes, budgets, investments, goals, notifications) for a clean slate."""
    from app.models.income import Income
    from app.models.expense import Expense
    from app.models.budget import Budget
    from app.models.investment import Investment
    from app.models.goal import Goal
    from app.models.notification import Notification

    user_id = current_user.id
    Income.query.filter_by(user_id=user_id).delete()
    Expense.query.filter_by(user_id=user_id).delete()
    Budget.query.filter_by(user_id=user_id).delete()
    Investment.query.filter_by(user_id=user_id).delete()
    Goal.query.filter_by(user_id=user_id).delete()
    Notification.query.filter_by(user_id=user_id).delete()

    db.session.commit()
    flash('All expenses, budgets, and pre-filled data have been cleared. Your account is now completely clean!', 'success')
    return redirect(url_for('dashboard.index'))
