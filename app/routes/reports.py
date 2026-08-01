import os
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, flash, current_app, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.report import Report
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.goal import Goal
from app.services.health_score import calculate_financial_health_score
from app.services.pdf_generator import generate_financial_pdf_report
from app.services.exporter import export_transactions_csv, export_transactions_excel

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['GET'])
@login_required
def index():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.generated_at.desc()).all()
    return render_template('reports/index.html', reports=reports, report_types=Report.REPORT_TYPES)


@reports_bp.route('/generate-pdf', methods=['POST'])
@login_required
def generate_pdf():
    report_type = request.form.get('report_type', 'Monthly Report')

    user_id = current_user.id
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()
    investments = Investment.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()

    total_inc = sum(i.amount for i in incomes)
    total_exp = sum(e.amount for e in expenses)
    total_sav = total_inc - total_exp
    total_inv = sum(inv.current_value for inv in investments)

    health_score_data = calculate_financial_health_score(
        current_user, total_inc, total_exp, total_sav, total_inv, budgets, goals
    )

    filename = f"Financial_Report_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(current_app.config['REPORTS_DIR'], filename)

    try:
        generate_financial_pdf_report(
            user=current_user,
            report_type=report_type,
            incomes=incomes,
            expenses=expenses,
            budgets=budgets,
            investments=investments,
            goals=goals,
            health_score_data=health_score_data,
            output_path=file_path
        )

        new_report = Report(
            user_id=user_id,
            title=f"{report_type} - {datetime.now().strftime('%b %Y')}",
            report_type=report_type,
            format='PDF',
            file_path=file_path
        )
        db.session.add(new_report)
        db.session.commit()

        flash('PDF Financial Report generated successfully!', 'success')
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Failed to generate PDF report: {str(e)}', 'danger')
        return redirect(url_for('reports.index'))


@reports_bp.route('/export/csv')
@login_required
def export_csv():
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    csv_data = export_transactions_csv(incomes, expenses)
    filename = f"PFM_Transactions_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route('/export/excel')
@login_required
def export_excel():
    user_id = current_user.id
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()
    investments = Investment.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()

    excel_data = export_transactions_excel(incomes, expenses, budgets, investments, goals)
    filename = f"PFM_Financial_Statement_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return send_file(
        excel_data,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
