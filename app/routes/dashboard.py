from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.goal import Goal
from app.models.notification import Notification
from app.services.health_score import calculate_financial_health_score
from app.services.notification_service import check_and_generate_notifications

dashboard_bp = Blueprint('dashboard', __name__)

import calendar

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = current_user.id
    today = date.today()

    # Time Boundaries
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = date(today.year, today.month, 1)
    _, last_day = calendar.monthrange(today.year, today.month)
    end_of_month = date(today.year, today.month, last_day)
    start_of_quarter = date(today.year, 3 * ((today.month - 1) // 3) + 1, 1)
    start_of_year = date(today.year, 1, 1)

    # Fetch User Records
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id, month=today.month, year=today.year).all()
    investments = Investment.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    # Aggregations
    total_income = sum(i.amount for i in incomes)

    weekly_expenses = sum(e.amount for e in expenses if e.date >= start_of_week)
    monthly_expenses = sum(e.amount for e in expenses if start_of_month <= e.date <= end_of_month)
    quarterly_expenses = sum(e.amount for e in expenses if e.date >= start_of_quarter)
    yearly_expenses = sum(e.amount for e in expenses if e.date >= start_of_year)
    total_expenses = sum(e.amount for e in expenses)

    # Savings = Income - Expenses
    weekly_income = sum(i.amount for i in incomes if i.date >= start_of_week)
    monthly_income = sum(i.amount for i in incomes if start_of_month <= i.date <= end_of_month)
    quarterly_income = sum(i.amount for i in incomes if i.date >= start_of_quarter)
    yearly_income = sum(i.amount for i in incomes if i.date >= start_of_year)

    weekly_savings = weekly_income - weekly_expenses
    monthly_savings = monthly_income - monthly_expenses
    quarterly_savings = quarterly_income - quarterly_expenses
    yearly_savings = yearly_income - yearly_expenses
    total_savings = total_income - total_expenses
    savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0.0

    # Budget Calculations
    overall_budget = sum(b.monthly_limit for b in budgets)
    budget_remaining = max(0.0, overall_budget - monthly_expenses)
    budget_used_pct = (monthly_expenses / overall_budget * 100) if overall_budget > 0 else 0.0

    # Investments
    total_investment_amount = sum(inv.current_value for inv in investments)

    # Goals
    total_goals_target = sum(g.target_amount for g in goals)
    total_goals_current = sum(g.current_amount for g in goals)
    overall_goal_progress = (total_goals_current / total_goals_target * 100) if total_goals_target > 0 else 0.0

    # Financial Health Score
    health_score_data = calculate_financial_health_score(
        current_user, monthly_income, monthly_expenses, monthly_savings,
        total_investment_amount, budgets, goals
    )

    # Trigger Notifications check
    check_and_generate_notifications(
        current_user, monthly_income, monthly_expenses, budgets, goals, savings_rate
    )

    # Recent Transactions (5 Incomes + 5 Expenses combined)
    recent_incomes = [{'type': 'Income', 'title': i.title, 'amount': i.amount, 'category': i.category, 'date': i.date, 'class': 'text-success'} for i in incomes]
    recent_expenses = [{'type': 'Expense', 'title': e.title, 'amount': e.amount, 'category': e.category, 'date': e.date, 'class': 'text-danger'} for e in expenses]
    recent_transactions = sorted(recent_incomes + recent_expenses, key=lambda x: x['date'], reverse=True)[:7]

    # Chart Data Preparation
    # Expense by Category
    exp_category_totals = {}
    for e in expenses:
        exp_category_totals[e.category] = exp_category_totals.get(e.category, 0.0) + e.amount

    # Investment by Type
    inv_type_totals = {}
    for inv in investments:
        inv_type_totals[inv.type] = inv_type_totals.get(inv.type, 0.0) + inv.current_value

    return render_template(
        'dashboard/index.html',
        total_income=total_income,
        monthly_income=monthly_income,
        weekly_expenses=weekly_expenses,
        monthly_expenses=monthly_expenses,
        quarterly_expenses=quarterly_expenses,
        yearly_expenses=yearly_expenses,
        weekly_savings=weekly_savings,
        monthly_savings=monthly_savings,
        quarterly_savings=quarterly_savings,
        yearly_savings=yearly_savings,
        savings_rate=savings_rate,
        overall_budget=overall_budget,
        budget_remaining=budget_remaining,
        budget_used_pct=budget_used_pct,
        total_investment_amount=total_investment_amount,
        overall_goal_progress=overall_goal_progress,
        health_score=health_score_data,
        recent_transactions=recent_transactions,
        notifications=notifications,
        unread_count=unread_count,
        exp_categories=list(exp_category_totals.keys()),
        exp_category_values=list(exp_category_totals.values()),
        inv_types=list(inv_type_totals.keys()),
        inv_type_values=list(inv_type_totals.values())
    )


@dashboard_bp.route('/notifications/mark-read/<int:id>', methods=['POST'])
@login_required
def mark_notification_read(id):
    notif = Notification.query.filter_by(id=id, user_id=current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404
