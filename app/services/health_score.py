"""
Financial Health Score Calculator
Evaluates financial wellness on a 0-100 scale using 6 key pillars:
1. Savings Rate (Max 25 pts)
2. Budget Compliance (Max 20 pts)
3. Investment Consistency / Ratio (Max 20 pts)
4. Emergency Fund Ratio (Max 15 pts)
5. Goal Progress (Max 10 pts)
6. Spending Stability (Max 10 pts)
"""

def calculate_financial_health_score(user, total_income, total_expense, total_savings, total_investments, budgets, goals):
    score = 0.0
    breakdown = {}

    # Pillar 1: Savings Rate (25 Points)
    # Target: 20-30%+ savings rate gets full points
    savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
    if savings_rate >= 30:
        savings_score = 25.0
    elif savings_rate >= 20:
        savings_score = 20.0
    elif savings_rate >= 10:
        savings_score = 12.0
    elif savings_rate > 0:
        savings_score = 5.0
    else:
        savings_score = 0.0
    score += savings_score
    breakdown['Savings Rate'] = {'score': savings_score, 'max': 25, 'value': f"{savings_rate:.1f}%"}

    # Pillar 2: Budget Compliance (20 Points)
    overall_budget = sum(b.monthly_limit for b in budgets) if budgets else 0
    if overall_budget > 0:
        usage_pct = (total_expense / overall_budget) * 100
        if usage_pct <= 80:
            budget_score = 20.0
        elif usage_pct <= 100:
            budget_score = 15.0
        elif usage_pct <= 115:
            budget_score = 5.0
        else:
            budget_score = 0.0
    else:
        # If no budget set, default neutral score
        budget_score = 10.0
        usage_pct = 0
    score += budget_score
    breakdown['Budget Usage'] = {'score': budget_score, 'max': 20, 'value': f"{usage_pct:.1f}% used"}

    # Pillar 3: Investment Ratio (20 Points)
    # Target: Investing 15%+ of income into investments
    investment_ratio = (total_investments / total_income * 100) if total_income > 0 else 0
    if investment_ratio >= 20:
        invest_score = 20.0
    elif investment_ratio >= 10:
        invest_score = 14.0
    elif investment_ratio > 0:
        invest_score = 8.0
    else:
        invest_score = 0.0
    score += invest_score
    breakdown['Investment Ratio'] = {'score': invest_score, 'max': 20, 'value': f"{investment_ratio:.1f}%"}

    # Pillar 4: Emergency Fund (15 Points)
    # Target: Liquid savings/FD/Gold >= 3 to 6 months of expenses
    monthly_expense_approx = total_expense if total_expense > 0 else 1.0
    emergency_months = total_savings / monthly_expense_approx if monthly_expense_approx > 0 else 0
    if emergency_months >= 6:
        emergency_score = 15.0
    elif emergency_months >= 3:
        emergency_score = 10.0
    elif emergency_months >= 1:
        emergency_score = 5.0
    else:
        emergency_score = 2.0
    score += emergency_score
    breakdown['Emergency Fund'] = {'score': emergency_score, 'max': 15, 'value': f"{emergency_months:.1f} months"}

    # Pillar 5: Goal Progress (10 Points)
    if goals:
        avg_completion = sum(g.completion_percentage for g in goals) / len(goals)
        goal_score = round((avg_completion / 100.0) * 10.0, 1)
    else:
        goal_score = 5.0
        avg_completion = 0.0
    score += goal_score
    breakdown['Goal Progress'] = {'score': goal_score, 'max': 10, 'value': f"{avg_completion:.1f}% avg"}

    # Pillar 6: Spending Stability (10 Points)
    # If expenses do not exceed income, full points
    if total_income >= total_expense:
        stability_score = 10.0
    else:
        stability_score = 0.0
    score += stability_score
    breakdown['Spending Stability'] = {'score': stability_score, 'max': 10, 'value': 'Stable' if stability_score > 0 else 'Deficit'}

    final_score = int(round(score))

    if final_score >= 90:
        grade = 'Excellent'
        badge_color = 'success'
        summary_msg = "Outstanding financial health! Your savings, investments, and spending are perfectly balanced."
    elif final_score >= 75:
        grade = 'Good'
        badge_color = 'primary'
        summary_msg = "Strong financial health. You are on track with solid savings and budget management."
    elif final_score >= 50:
        grade = 'Average'
        badge_color = 'warning'
        summary_msg = "Fair financial health. Focus on lowering discretionary expenses and boosting investments."
    else:
        grade = 'Needs Improvement'
        badge_color = 'danger'
        summary_msg = "Immediate action needed! Your expenses exceed recommended thresholds or savings are low."

    return {
        'score': final_score,
        'grade': grade,
        'badge_color': badge_color,
        'summary': summary_msg,
        'breakdown': breakdown
    }
