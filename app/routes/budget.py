from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.budget import Budget
from app.models.expense import Expense

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/', methods=['GET'])
@login_required
def index():
    today = date.today()
    selected_month = int(request.args.get('month', today.month))
    selected_year = int(request.args.get('year', today.year))

    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month,
        year=selected_year
    ).all()

    # Get Expenses for selected Month & Year
    start_date = date(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1)
    else:
        end_date = date(selected_year, selected_month + 1, 1)

    month_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date < end_date
    ).all()

    # Aggregate Expenses by Category
    exp_by_cat = {}
    total_month_spent = sum(e.amount for e in month_expenses)
    for e in month_expenses:
        exp_by_cat[e.category] = exp_by_cat.get(e.category, 0.0) + e.amount

    # Build Budget Analysis Items
    budget_items = []
    total_budget_limit = 0.0

    for b in budgets:
        total_budget_limit += b.monthly_limit
        if b.category == 'Overall':
            spent = total_month_spent
        else:
            spent = exp_by_cat.get(b.category, 0.0)

        remaining = max(0.0, b.monthly_limit - spent)
        used_pct = (spent / b.monthly_limit * 100) if b.monthly_limit > 0 else 0.0

        if used_pct >= 100:
            status_badge = 'danger'
            status_text = 'Exceeded'
        elif used_pct >= 85:
            status_badge = 'warning'
            status_text = 'Near Limit'
        else:
            status_badge = 'success'
            status_text = 'On Track'

        budget_items.append({
            'budget': b,
            'spent': spent,
            'remaining': remaining,
            'used_pct': min(100.0, used_pct),
            'actual_pct': used_pct,
            'status_badge': status_badge,
            'status_text': status_text
        })

    overall_remaining = max(0.0, total_budget_limit - total_month_spent)
    overall_used_pct = (total_month_spent / total_budget_limit * 100) if total_budget_limit > 0 else 0.0

    return render_template(
        'budget/index.html',
        budget_items=budget_items,
        categories=['Overall'] + Expense.CATEGORIES,
        selected_month=selected_month,
        selected_year=selected_year,
        total_budget_limit=total_budget_limit,
        total_month_spent=total_month_spent,
        overall_remaining=overall_remaining,
        overall_used_pct=overall_used_pct
    )


@budget_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    category = request.form.get('category', 'Overall')
    monthly_limit = float(request.form.get('monthly_limit', 0.0) or 0.0)
    month = int(request.form.get('month', date.today().month))
    year = int(request.form.get('year', date.today().year))

    if monthly_limit <= 0:
        flash('Budget limit must be greater than zero.', 'danger')
        return redirect(url_for('budget.index', month=month, year=year))

    existing = Budget.query.filter_by(
        user_id=current_user.id,
        category=category,
        month=month,
        year=year
    ).first()

    if existing:
        existing.monthly_limit = monthly_limit
        flash(f'Updated budget limit for {category}.', 'success')
    else:
        new_b = Budget(
            user_id=current_user.id,
            category=category,
            monthly_limit=monthly_limit,
            month=month,
            year=year
        )
        db.session.add(new_b)
        flash(f'New budget limit set for {category}.', 'success')

    db.session.commit()
    return redirect(url_for('budget.index', month=month, year=year))


@budget_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    b = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    month, year = b.month, b.year
    db.session.delete(b)
    db.session.commit()
    flash('Budget limit deleted.', 'info')
    return redirect(url_for('budget.index', month=month, year=year))
