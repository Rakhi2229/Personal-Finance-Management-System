import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from datetime import datetime, timedelta

def predict_future_expenses(expenses, current_monthly_budget=0.0):
    """
    Uses Scikit-Learn machine learning model (Ridge / Linear Regression)
    to forecast Next Week, Next Month, and Next Quarter expenses.
    Generates intelligent warnings and trend analysis.
    """
    if not expenses or len(expenses) < 3:
        # Fallback for small sample size
        total_spent = sum(e.amount for e in expenses) if expenses else 0.0
        avg_weekly = (total_spent / max(1, len(expenses))) * 7
        return {
            'next_week': round(avg_weekly, 2),
            'next_month': round(avg_weekly * 4.33, 2),
            'next_quarter': round(avg_weekly * 13, 2),
            'trend_percentage': 0.0,
            'warnings': ["Add more expense transactions for higher accuracy AI predictions."],
            'sufficient_data': False
        }

    # Convert expenses to pandas DataFrame
    data = []
    for e in expenses:
        data.append({
            'date': pd.to_datetime(e.date),
            'amount': float(e.amount)
        })

    df = pd.DataFrame(data)
    df = df.sort_values('date')

    # Aggregate by daily sum
    daily_df = df.groupby('date')['amount'].sum().reset_index()

    # Create full date range sequence to handle missing days with 0
    full_idx = pd.date_range(start=daily_df['date'].min(), end=daily_df['date'].max())
    daily_df = daily_df.set_index('date').reindex(full_idx, fill_value=0.0).reset_index()
    daily_df.rename(columns={'index': 'date'}, inplace=True)

    # Feature Engineering: Ordinal days from start
    start_date = daily_df['date'].min()
    daily_df['day_num'] = (daily_df['date'] - start_date).dt.days

    X = daily_df[['day_num']].values
    y = daily_df['amount'].values

    # Train Scikit-Learn Regression Model
    model = Ridge(alpha=1.0)
    model.fit(X, y)

    last_day = daily_df['day_num'].max()

    # Forecast Next 7 Days (Next Week)
    next_week_x = np.array([[last_day + i] for i in range(1, 8)])
    pred_next_week = max(0.0, float(np.sum(model.predict(next_week_x))))

    # Forecast Next 30 Days (Next Month)
    next_month_x = np.array([[last_day + i] for i in range(1, 31)])
    pred_next_month = max(0.0, float(np.sum(model.predict(next_month_x))))

    # Forecast Next 90 Days (Next Quarter)
    next_quarter_x = np.array([[last_day + i] for i in range(1, 91)])
    pred_next_quarter = max(0.0, float(np.sum(model.predict(next_quarter_x))))

    # Trend calculation compared to historical 30-day average
    recent_30_days = y[-30:] if len(y) >= 30 else y
    recent_monthly_avg = float(np.sum(recent_30_days))
    if recent_monthly_avg > 0:
        trend_pct = round(((pred_next_month - recent_monthly_avg) / recent_monthly_avg) * 100, 1)
    else:
        trend_pct = 0.0

    warnings = []
    if trend_pct > 5:
        warnings.append(f"⚠️ Your expenses are likely to increase by {trend_pct}% next month based on spending velocity.")
    elif trend_pct < -5:
        warnings.append(f"🎉 Great job! AI forecasts a {abs(trend_pct)}% drop in spending next month.")

    if current_monthly_budget > 0 and pred_next_month > current_monthly_budget:
        over_amt = pred_next_month - current_monthly_budget
        warnings.append(f"🚨 Budget Risk: Predicted next month expense (₹{pred_next_month:,.2f}) exceeds your budget limit (₹{current_monthly_budget:,.2f}) by ₹{over_amt:,.2f}!")

    return {
        'next_week': round(pred_next_week, 2),
        'next_month': round(pred_next_month, 2),
        'next_quarter': round(pred_next_quarter, 2),
        'trend_percentage': trend_pct,
        'warnings': warnings,
        'sufficient_data': True
    }
