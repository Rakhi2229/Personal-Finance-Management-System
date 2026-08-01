import io
import pandas as pd

def export_transactions_csv(incomes, expenses):
    """
    Exports combined income and expense history to a clean CSV format.
    """
    records = []

    for inc in incomes:
        records.append({
            'Type': 'INCOME',
            'Date': inc.date.strftime('%Y-%m-%d'),
            'Title': inc.title,
            'Category': inc.category,
            'Amount (INR)': inc.amount,
            'Payment Method': inc.payment_method,
            'Notes': inc.notes or ''
        })

    for exp in expenses:
        records.append({
            'Type': 'EXPENSE',
            'Date': exp.date.strftime('%Y-%m-%d'),
            'Title': exp.title,
            'Category': exp.category,
            'Amount (INR)': -exp.amount,  # Negative for expense
            'Payment Method': exp.payment_method,
            'Notes': exp.notes or ''
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values('Date', ascending=False)

    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output


def export_transactions_excel(incomes, expenses, budgets, investments, goals):
    """
    Exports comprehensive financial dataset with multiple styled Excel sheets using OpenPyXL.
    """
    output = io.BytesIO()

    # Sheet 1: Incomes
    inc_df = pd.DataFrame([{
        'ID': i.id, 'Date': i.date.strftime('%Y-%m-%d'), 'Title': i.title,
        'Category': i.category, 'Amount (INR)': i.amount, 'Payment Method': i.payment_method, 'Notes': i.notes or ''
    } for i in incomes])

    # Sheet 2: Expenses
    exp_df = pd.DataFrame([{
        'ID': e.id, 'Date': e.date.strftime('%Y-%m-%d'), 'Title': e.title,
        'Category': e.category, 'Amount (INR)': e.amount, 'Payment Method': e.payment_method,
        'Auto Classified': 'Yes' if e.auto_classified else 'No', 'Notes': e.notes or ''
    } for e in expenses])

    # Sheet 3: Investments
    inv_df = pd.DataFrame([{
        'ID': inv.id, 'Title': inv.title, 'Type': inv.type,
        'Invested (INR)': inv.amount_invested, 'Current Value (INR)': inv.current_value,
        'Return (INR)': inv.absolute_return, 'Return (%)': inv.percentage_return,
        'Start Date': inv.start_date.strftime('%Y-%m-%d')
    } for inv in investments])

    # Sheet 4: Goals
    goal_df = pd.DataFrame([{
        'ID': g.id, 'Title': g.title, 'Category': g.category,
        'Target (INR)': g.target_amount, 'Saved (INR)': g.current_amount,
        'Progress (%)': g.completion_percentage, 'Target Date': g.target_date.strftime('%Y-%m-%d')
    } for g in goals])

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        inc_df.to_excel(writer, sheet_name='Income History', index=False)
        exp_df.to_excel(writer, sheet_name='Expense History', index=False)
        inv_df.to_excel(writer, sheet_name='Investments', index=False)
        goal_df.to_excel(writer, sheet_name='Goals Progress', index=False)

    output.seek(0)
    return output
