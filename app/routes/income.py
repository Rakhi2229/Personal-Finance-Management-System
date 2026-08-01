from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.income import Income

income_bp = Blueprint('income', __name__)

@income_bp.route('/', methods=['GET'])
@login_required
def index():
    query = Income.query.filter_by(user_id=current_user.id)

    # Search & Filter Parameters
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    if search:
        query = query.filter(Income.title.ilike(f"%{search}%"))

    if category:
        query = query.filter(Income.category == category)

    if start_date:
        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Income.date >= s_date)
        except ValueError:
            pass

    if end_date:
        try:
            e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Income.date <= e_date)
        except ValueError:
            pass

    incomes = query.order_by(Income.date.desc()).all()
    total_amount = sum(i.amount for i in incomes)

    return render_template(
        'income/index.html',
        incomes=incomes,
        categories=Income.CATEGORIES,
        total_amount=total_amount,
        search=search,
        selected_category=category,
        start_date=start_date,
        end_date=end_date
    )


@income_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    amount = float(request.form.get('amount', 0.0) or 0.0)
    category = request.form.get('category', 'Salary')
    payment_method = request.form.get('payment_method', 'Bank Transfer')
    income_date_str = request.form.get('date', '')
    notes = request.form.get('notes', '').strip()

    if not title or amount <= 0:
        flash('Title and valid amount are required.', 'danger')
        return redirect(url_for('income.index'))

    try:
        inc_date = datetime.strptime(income_date_str, '%Y-%m-%d').date() if income_date_str else date.today()
    except ValueError:
        inc_date = date.today()

    new_income = Income(
        user_id=current_user.id,
        title=title,
        amount=amount,
        category=category,
        payment_method=payment_method,
        date=inc_date,
        notes=notes
    )
    db.session.add(new_income)
    db.session.commit()
    flash('Income record added successfully!', 'success')
    return redirect(url_for('income.index'))


@income_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    inc = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    inc.title = request.form.get('title', inc.title).strip()
    inc.amount = float(request.form.get('amount', inc.amount) or 0.0)
    inc.category = request.form.get('category', inc.category)
    inc.payment_method = request.form.get('payment_method', inc.payment_method)
    notes = request.form.get('notes', '').strip()
    inc.notes = notes

    income_date_str = request.form.get('date', '')
    if income_date_str:
        try:
            inc.date = datetime.strptime(income_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db.session.commit()
    flash('Income record updated successfully!', 'success')
    return redirect(url_for('income.index'))


@income_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    inc = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(inc)
    db.session.commit()
    flash('Income record deleted.', 'info')
    return redirect(url_for('income.index'))
