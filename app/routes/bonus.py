import io
import json
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.goal import Goal
from app.services.ocr_service import parse_receipt_text
from app.services.gamification_service import evaluate_user_achievements

bonus_bp = Blueprint('bonus', __name__)

@bonus_bp.route('/hub', methods=['GET'])
@login_required
def index():
    """Central Hub for bonus features: Receipt OCR, Achievements, Growth Simulator, Admin & Backup."""
    user_id = current_user.id
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()
    investments = Investment.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()

    # Gamification
    gamification = evaluate_user_achievements(current_user, incomes, expenses, budgets, investments, goals)

    # Admin Summary Stats (Global Platform Metrics)
    total_system_users = User.query.count()
    total_system_incomes = Income.query.count()
    total_system_expenses = Expense.query.count()
    total_system_volume = sum(i.amount for i in Income.query.all()) + sum(e.amount for e in Expense.query.all())

    return render_template(
        'bonus/index.html',
        gamification=gamification,
        total_system_users=total_system_users,
        total_system_incomes=total_system_incomes,
        total_system_expenses=total_system_expenses,
        total_system_volume=total_system_volume
    )


@bonus_bp.route('/scan-receipt', methods=['POST'])
@login_required
def scan_receipt():
    """OCR Receipt Parser API - processes receipt text input or file snippet."""
    receipt_text = request.form.get('receipt_text', '')
    if not receipt_text and 'receipt_file' in request.files:
        file = request.files['receipt_file']
        if file and file.filename:
            # Read snippet text content from uploaded text/image file
            receipt_text = file.read().decode('utf-8', errors='ignore')

    result = parse_receipt_text(receipt_text)

    # Save automatically as a new expense entry if requested
    if request.form.get('auto_save'):
        new_exp = Expense(
            user_id=current_user.id,
            title=result['title'],
            amount=result['amount'],
            category=result['category'],
            payment_method='UPI',
            date=date.today(),
            notes='Auto-scanned via OCR Receipt Scanner',
            auto_classified=result['auto_classified']
        )
        db.session.add(new_exp)
        db.session.commit()
        flash(f'Receipt scanned and saved as expense: {result["title"]} - ₹{result["amount"]:.2f} ({result["category"]})', 'success')
        return redirect(url_for('expense.index'))

    return jsonify(result)


@bonus_bp.route('/growth-simulator', methods=['POST'])
@login_required
def growth_simulator():
    """Multi-decade Wealth Simulator with Inflation Adjustment."""
    data = request.get_json() or {}
    monthly_investment = float(data.get('monthly_investment', 10000))
    initial_principal = float(data.get('initial_principal', 50000))
    expected_cagr = float(data.get('cagr', 12.0))
    inflation_rate = float(data.get('inflation', 6.0))
    years = int(data.get('years', 20))

    real_rate = expected_cagr - inflation_rate
    monthly_real_rate = (real_rate / 100.0) / 12.0
    total_months = years * 12

    trajectory = []
    current_nominal = initial_principal
    current_real = initial_principal

    for y in range(1, years + 1):
        # Calculate end of year wealth
        m_rate = (expected_cagr / 100.0) / 12.0
        m_real = (real_rate / 100.0) / 12.0

        for m in range(12):
            current_nominal = (current_nominal + monthly_investment) * (1 + m_rate)
            current_real = (current_real + monthly_investment) * (1 + m_real)

        trajectory.append({
            'year': f"Year {y}",
            'nominal_wealth': round(current_nominal, 2),
            'real_wealth': round(current_real, 2),
            'total_invested': round(initial_principal + (monthly_investment * 12 * y), 2)
        })

    return jsonify({'trajectory': trajectory})


@bonus_bp.route('/backup/download')
@login_required
def download_backup():
    """Downloads a complete JSON backup of the user's financial dataset."""
    user_id = current_user.id
    backup_data = {
        'version': '1.0',
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user': current_user.to_dict(),
        'incomes': [i.to_dict() for i in Income.query.filter_by(user_id=user_id).all()],
        'expenses': [e.to_dict() for e in Expense.query.filter_by(user_id=user_id).all()],
        'budgets': [b.to_dict() for b in Budget.query.filter_by(user_id=user_id).all()],
        'investments': [inv.to_dict() for inv in Investment.query.filter_by(user_id=user_id).all()],
        'goals': [g.to_dict() for g in Goal.query.filter_by(user_id=user_id).all()]
    }

    output = io.BytesIO()
    output.write(json.dumps(backup_data, indent=2).encode('utf-8'))
    output.seek(0)

    filename = f"PFM_Backup_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.json"
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )
