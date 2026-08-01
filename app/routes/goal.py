from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.goal import Goal

goal_bp = Blueprint('goal', __name__)

@goal_bp.route('/', methods=['GET'])
@login_required
def index():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.target_date.asc()).all()

    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_pct = (total_saved / total_target * 100) if total_target > 0 else 0.0
    total_monthly_needed = sum(g.monthly_contribution_needed for g in goals)

    return render_template(
        'goal/index.html',
        goals=goals,
        categories=Goal.CATEGORIES,
        total_target=total_target,
        total_saved=total_saved,
        overall_pct=overall_pct,
        total_monthly_needed=total_monthly_needed
    )


@goal_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Others')
    target_amount = float(request.form.get('target_amount', 0.0) or 0.0)
    current_amount = float(request.form.get('current_amount', 0.0) or 0.0)
    target_date_str = request.form.get('target_date', '')

    if not title or target_amount <= 0 or not target_date_str:
        flash('Goal title, valid target amount, and target date are required.', 'danger')
        return redirect(url_for('goal.index'))

    try:
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid target date format.', 'danger')
        return redirect(url_for('goal.index'))

    new_goal = Goal(
        user_id=current_user.id,
        title=title,
        category=category,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date
    )
    db.session.add(new_goal)
    db.session.commit()
    flash(f'Financial Goal "{title}" created successfully!', 'success')
    return redirect(url_for('goal.index'))


@goal_bp.route('/add-funds/<int:id>', methods=['POST'])
@login_required
def add_funds(id):
    g = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    add_amount = float(request.form.get('amount', 0.0) or 0.0)

    if add_amount > 0:
        g.current_amount += add_amount
        db.session.commit()
        flash(f'Added ₹{add_amount:,.2f} to goal "{g.title}".', 'success')
    else:
        flash('Please enter a valid contribution amount.', 'warning')

    return redirect(url_for('goal.index'))


@goal_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    g = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    g.title = request.form.get('title', g.title).strip()
    g.category = request.form.get('category', g.category)
    g.target_amount = float(request.form.get('target_amount', g.target_amount) or 0.0)
    g.current_amount = float(request.form.get('current_amount', g.current_amount) or 0.0)

    target_date_str = request.form.get('target_date', '')
    if target_date_str:
        try:
            g.target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db.session.commit()
    flash('Goal details updated.', 'success')
    return redirect(url_for('goal.index'))


@goal_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    g = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(g)
    db.session.commit()
    flash('Goal deleted.', 'info')
    return redirect(url_for('goal.index'))
