from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.services.ai_predictor import predict_future_expenses
from app.services.smart_budget import generate_smart_budget_recommendation
from app.services.ai_classifier import classify_expense_title

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = current_user.id
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.asc()).all()
    incomes = Income.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()

    today = date.today()
    start_of_month = date(today.year, today.month, 1)

    monthly_income = sum(i.amount for i in incomes if i.date >= start_of_month)
    monthly_expense = sum(e.amount for e in expenses if e.date >= start_of_month)
    overall_budget = sum(b.monthly_limit for b in budgets)

    # 1. AI Spending Predictor
    prediction_data = predict_future_expenses(expenses, current_monthly_budget=overall_budget)

    # 2. AI Smart Budget Planner
    smart_budget_recommendation = generate_smart_budget_recommendation(monthly_income, historical_expenses=expenses)

    # 3. Dynamic Financial Insights Generation
    insights = []
    total_inc = sum(i.amount for i in incomes)
    total_exp = sum(e.amount for e in expenses)
    net_sav = total_inc - total_exp
    sav_rate = (net_sav / total_inc * 100) if total_inc > 0 else 0.0

    if sav_rate > 0:
        insights.append({
            'type': 'success',
            'title': 'Savings Rate Milestone',
            'message': f'🎉 You saved {sav_rate:.1f}% of your overall income!'
        })

    # Find highest expense category
    cat_spent = {}
    for e in expenses:
        cat_spent[e.category] = cat_spent.get(e.category, 0.0) + e.amount

    if cat_spent:
        top_cat = max(cat_spent.items(), key=lambda x: x[1])
        pct_top = (top_cat[1] / total_exp * 100) if total_exp > 0 else 0
        if pct_top > 30:
            insights.append({
                'type': 'warning',
                'title': 'High Spending Alert',
                'message': f'⚠️ You spent too much on {top_cat[0]} ({pct_top:.1f}% of total expenses). Try reducing {top_cat[0]} expenses by 15% next month.'
            })

    monthly_surplus = max(0.0, monthly_income - monthly_expense)
    if monthly_surplus > 2000:
        rec_sip = round(monthly_surplus * 0.5, -2)  # Round to nearest hundred
        insights.append({
            'type': 'info',
            'title': 'Investment Opportunity',
            'message': f'💡 Based on your surplus, you can comfortably invest ₹{rec_sip:,.0f} every month in Mutual Funds or Index Funds.'
        })

    return render_template(
        'ai/index.html',
        prediction=prediction_data,
        smart_budget=smart_budget_recommendation,
        insights=insights,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense
    )


@ai_bp.route('/apply-smart-budget', methods=['POST'])
@login_required
def apply_smart_budget():
    """Applies the AI recommended monthly budget into user's budget table."""
    user_id = current_user.id
    today = date.today()
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    start_of_month = date(today.year, today.month, 1)
    monthly_income = sum(i.amount for i in incomes if i.date >= start_of_month)

    rec = generate_smart_budget_recommendation(monthly_income, historical_expenses=expenses)

    # Insert or update budget limits for the current month
    for cat, limit in rec['category_allocations'].items():
        existing = Budget.query.filter_by(
            user_id=user_id,
            category=cat,
            month=today.month,
            year=today.year
        ).first()

        if existing:
            existing.monthly_limit = limit
        else:
            new_b = Budget(
                user_id=user_id,
                category=cat,
                monthly_limit=limit,
                month=today.month,
                year=today.year
            )
            db.session.add(new_b)

    db.session.commit()
    flash('AI Smart Budget allocation has been successfully applied to your monthly budget!', 'success')
    return redirect(url_for('budget.index'))
