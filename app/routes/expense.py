from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense
from app.services.ai_classifier import classify_expense_title

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/', methods=['GET'])
@login_required
def index():
    query = Expense.query.filter_by(user_id=current_user.id)

    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    payment_method = request.args.get('payment_method', '').strip()
    time_filter = request.args.get('time_filter', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    today = date.today()

    # Pre-defined Time Filter Ranges
    if time_filter == 'weekly':
        s_date = today - timedelta(days=today.weekday())
        query = query.filter(Expense.date >= s_date)
    elif time_filter == 'monthly':
        s_date = date(today.year, today.month, 1)
        query = query.filter(Expense.date >= s_date)
    elif time_filter == 'quarterly':
        s_date = today - timedelta(days=90)
        query = query.filter(Expense.date >= s_date)
    elif time_filter == 'yearly':
        s_date = date(today.year, 1, 1)
        query = query.filter(Expense.date >= s_date)

    if search:
        query = query.filter(Expense.title.ilike(f"%{search}%"))

    if category:
        query = query.filter(Expense.category == category)

    if payment_method:
        query = query.filter(Expense.payment_method == payment_method)

    if start_date:
        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= s_date)
        except ValueError:
            pass

    if end_date:
        try:
            e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= e_date)
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc()).all()
    total_amount = sum(e.amount for e in expenses)

    return render_template(
        'expense/index.html',
        expenses=expenses,
        categories=Expense.CATEGORIES,
        payment_methods=Expense.PAYMENT_METHODS,
        total_amount=total_amount,
        search=search,
        selected_category=category,
        selected_payment_method=payment_method,
        time_filter=time_filter,
        start_date=start_date,
        end_date=end_date
    )


@expense_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    amount = float(request.form.get('amount', 0.0) or 0.0)
    category = request.form.get('category', '').strip()
    payment_method = request.form.get('payment_method', 'UPI')
    exp_date_str = request.form.get('date', '')
    notes = request.form.get('notes', '').strip()

    if not title or amount <= 0:
        flash('Expense title and valid amount are required.', 'danger')
        return redirect(url_for('expense.index'))

    # AI Auto Classification if category is left as 'Auto' or blank
    auto_classified = False
    if not category or category == 'Auto':
        category, auto_classified = classify_expense_title(title)

    try:
        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date() if exp_date_str else date.today()
    except ValueError:
        exp_date = date.today()

    new_expense = Expense(
        user_id=current_user.id,
        title=title,
        amount=amount,
        category=category,
        payment_method=payment_method,
        date=exp_date,
        notes=notes,
        auto_classified=auto_classified
    )
    db.session.add(new_expense)
    db.session.commit()

    if auto_classified:
        flash(f'Expense added! AI auto-categorized "{title}" as {category}.', 'success')
    else:
        flash('Expense recorded successfully.', 'success')

    return redirect(url_for('expense.index'))


@expense_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    exp = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    exp.title = request.form.get('title', exp.title).strip()
    exp.amount = float(request.form.get('amount', exp.amount) or 0.0)
    exp.category = request.form.get('category', exp.category)
    exp.payment_method = request.form.get('payment_method', exp.payment_method)
    exp.notes = request.form.get('notes', '').strip()

    exp_date_str = request.form.get('date', '')
    if exp_date_str:
        try:
            exp.date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db.session.commit()
    flash('Expense updated successfully.', 'success')
    return redirect(url_for('expense.index'))


@expense_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    exp = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(exp)
    db.session.commit()
    flash('Expense deleted.', 'info')
    return redirect(url_for('expense.index'))


@expense_bp.route('/classify-preview', methods=['POST'])
@login_required
def classify_preview():
    data = request.get_json() or {}
    title = data.get('title', '')
    category, matched = classify_expense_title(title)
    return jsonify({'category': category, 'auto_classified': matched})
