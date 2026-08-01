from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.investment import Investment
from app.models.income import Income
from app.models.expense import Expense
from app.models.goal import Goal

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = current_user.id
    investments = Investment.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()

    # Core Portfolio Overview Aggregations
    total_invested = sum(i.amount_invested for i in investments)
    portfolio_value = sum(i.current_value for i in investments)
    total_gain = portfolio_value - total_invested
    portfolio_return_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0.0

    # Today's / Recent Gain Simulation
    todays_gain = round(portfolio_value * 0.0075, 2) if portfolio_value > 0 else 0.0
    todays_gain_pct = 0.75 if portfolio_value > 0 else 0.0

    # Passive Income Estimator (6.5% annual yield divided monthly)
    annual_passive = portfolio_value * 0.065
    monthly_passive = annual_passive / 12.0

    # Dynamic Timeframe Trajectories for Interactive Switcher
    timeframes_data = {
        '1D': {
            'labels': ['9:15 AM', '11:00 AM', '1:00 PM', '2:30 PM', '3:30 PM'],
            'data': [
                round(portfolio_value * 0.995, 2),
                round(portfolio_value * 0.998, 2),
                round(portfolio_value * 1.002, 2),
                round(portfolio_value * 1.005, 2),
                round(portfolio_value, 2)
            ] if portfolio_value > 0 else [0, 0, 0, 0, 0]
        },
        '1M': {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'data': [
                round(portfolio_value * 0.94, 2),
                round(portfolio_value * 0.96, 2),
                round(portfolio_value * 0.98, 2),
                round(portfolio_value, 2)
            ] if portfolio_value > 0 else [0, 0, 0, 0]
        },
        '6M': {
            'labels': ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            'data': [
                round(portfolio_value * 0.82, 2),
                round(portfolio_value * 0.88, 2),
                round(portfolio_value * 0.91, 2),
                round(portfolio_value * 0.95, 2),
                round(portfolio_value * 0.97, 2),
                round(portfolio_value, 2)
            ] if portfolio_value > 0 else [0, 0, 0, 0, 0, 0]
        },
        '1Y': {
            'labels': ['Aug', 'Oct', 'Dec', 'Feb', 'Apr', 'Jun', 'Jul'],
            'data': [
                round(portfolio_value * 0.75, 2),
                round(portfolio_value * 0.80, 2),
                round(portfolio_value * 0.84, 2),
                round(portfolio_value * 0.89, 2),
                round(portfolio_value * 0.93, 2),
                round(portfolio_value * 0.97, 2),
                round(portfolio_value, 2)
            ] if portfolio_value > 0 else [0, 0, 0, 0, 0, 0, 0]
        },
        'ALL': {
            'labels': ['2022', '2023', '2024', '2025', '2026'],
            'data': [
                round(portfolio_value * 0.50, 2),
                round(portfolio_value * 0.65, 2),
                round(portfolio_value * 0.80, 2),
                round(portfolio_value * 0.92, 2),
                round(portfolio_value, 2)
            ] if portfolio_value > 0 else [0, 0, 0, 0, 0]
        }
    }

    # Asset Allocation Donut Data
    asset_types = ['Stocks', 'Mutual Funds', 'Gold', 'FD', 'Crypto', 'Bonds', 'PPF', 'RD']
    allocation_dict = {t: 0.0 for t in asset_types}
    for inv in investments:
        inv_type = inv.type if inv.type in asset_types else 'Mutual Funds'
        allocation_dict[inv_type] += inv.current_value

    alloc_labels = [k for k, v in allocation_dict.items() if v > 0] or ['Mutual Funds']
    alloc_values = [v for k, v in allocation_dict.items() if v > 0] or [1]

    # Emergency Safety Shield
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    monthly_expense = sum(e.amount for e in Expense.query.filter(Expense.user_id == user_id, Expense.date >= start_of_month).all())
    
    target_emergency_amount = (monthly_expense or 25000.0) * 6
    liquid_current_amount = sum(inv.current_value for inv in investments if inv.type in ['FD', 'RD', 'Gold', 'Bonds'])
    emergency_remaining = max(0.0, target_emergency_amount - liquid_current_amount)
    emergency_pct = min(100.0, (liquid_current_amount / target_emergency_amount * 100)) if target_emergency_amount > 0 else 0.0

    safety_score = int(round(min(100.0, (emergency_pct * 0.7) + (portfolio_return_pct * 0.3 if portfolio_return_pct > 0 else 0))))
    if safety_score >= 80:
        safety_text = "Excellent Shield"
        safety_badge = "success"
    elif safety_score >= 50:
        safety_text = "Moderate Cushion"
        safety_badge = "warning"
    else:
        safety_text = "Action Needed"
        safety_badge = "danger"

    return render_template(
        'investment/index.html',
        investments=investments,
        investment_types=Investment.TYPES,
        total_invested=total_invested,
        portfolio_value=portfolio_value,
        total_gain=total_gain,
        portfolio_return_pct=portfolio_return_pct,
        todays_gain=todays_gain,
        todays_gain_pct=todays_gain_pct,
        monthly_passive=monthly_passive,
        annual_passive=annual_passive,
        timeframes_data=timeframes_data,
        alloc_labels=alloc_labels,
        alloc_values=alloc_values,
        target_emergency_amount=target_emergency_amount,
        liquid_current_amount=liquid_current_amount,
        emergency_remaining=emergency_remaining,
        emergency_pct=emergency_pct,
        safety_score=safety_score,
        safety_text=safety_text,
        safety_badge=safety_badge,
        goals=goals
    )


@investment_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    inv_type = request.form.get('type', 'Mutual Funds')
    amount_invested = float(request.form.get('amount_invested', 0.0) or 0.0)
    current_val = float(request.form.get('current_value', amount_invested) or amount_invested)
    expected_return_rate = float(request.form.get('expected_return_rate', 12.0) or 12.0)
    start_date_str = request.form.get('start_date', '')
    notes = request.form.get('notes', '').strip()

    if not title or amount_invested <= 0:
        flash('Valid asset title and invested amount are required.', 'danger')
        return redirect(url_for('investment.index'))

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today()
    except ValueError:
        start_date = date.today()

    new_inv = Investment(
        user_id=current_user.id,
        title=title,
        type=inv_type,
        amount_invested=amount_invested,
        current_value=current_val,
        expected_return_rate=expected_return_rate,
        start_date=start_date,
        notes=notes
    )
    db.session.add(new_inv)
    db.session.commit()
    flash('New investment added to portfolio!', 'success')
    return redirect(url_for('investment.index'))


@investment_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    inv = Investment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(inv)
    db.session.commit()
    flash('Investment removed from portfolio.', 'info')
    return redirect(url_for('investment.index'))


@investment_bp.route('/calculate-wealth', methods=['POST'])
@login_required
def calculate_wealth():
    data = request.get_json() or {}
    monthly_sip = float(data.get('monthly_sip', 10000))
    initial_lump = float(data.get('initial_lump', 50000))
    annual_rate = float(data.get('annual_rate', 12.0))
    years = int(data.get('years', 10))

    monthly_rate = annual_rate / 12.0 / 100.0
    total_months = years * 12

    future_lump = initial_lump * ((1 + monthly_rate) ** total_months)
    if monthly_rate > 0:
        future_sip = monthly_sip * (((1 + monthly_rate) ** total_months - 1) / monthly_rate) * (1 + monthly_rate)
    else:
        future_sip = monthly_sip * total_months

    total_wealth = round(future_lump + future_sip, 2)
    total_invested = round(initial_lump + (monthly_sip * total_months), 2)
    estimated_returns = round(total_wealth - total_invested, 2)

    return jsonify({
        'total_wealth': total_wealth,
        'total_invested': total_invested,
        'estimated_returns': estimated_returns
    })
