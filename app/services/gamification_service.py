"""
Gamification & Achievement Badge Evaluator Engine
Evaluates user activity and awards badges & monthly challenge scores.
"""

def evaluate_user_achievements(user, incomes, expenses, budgets, investments, goals):
    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
    total_invested = sum(inv.current_value for inv in investments)

    badges = []

    # Badge 1: Super Saver (30%+ Savings Rate)
    if savings_rate >= 30:
        badges.append({
            'title': 'Super Saver',
            'icon': 'fa-solid fa-piggy-bank text-warning',
            'description': 'Achieved an outstanding 30%+ monthly savings rate!',
            'unlocked': True
        })
    else:
        badges.append({
            'title': 'Super Saver',
            'icon': 'fa-solid fa-piggy-bank text-muted',
            'description': 'Reach 30% savings rate to unlock.',
            'unlocked': False
        })

    # Badge 2: Budget Guardian (Maintained budget limits)
    overall_budget = sum(b.monthly_limit for b in budgets)
    if overall_budget > 0 and total_expense <= overall_budget:
        badges.append({
            'title': 'Budget Guardian',
            'icon': 'fa-solid fa-shield-halved text-success',
            'description': 'Stayed strictly within set monthly budget limits!',
            'unlocked': True
        })
    else:
        badges.append({
            'title': 'Budget Guardian',
            'icon': 'fa-solid fa-shield-halved text-muted',
            'description': 'Keep total expenses under your budget limit.',
            'unlocked': False
        })

    # Badge 3: Portfolio Builder (Investments > ₹1,00,000)
    if total_invested >= 100000:
        badges.append({
            'title': 'Portfolio Builder',
            'icon': 'fa-solid fa-chart-line text-info',
            'description': 'Built an investment portfolio exceeding ₹1,00,000!',
            'unlocked': True
        })
    else:
        badges.append({
            'title': 'Portfolio Builder',
            'icon': 'fa-solid fa-chart-line text-muted',
            'description': 'Grow total investment value above ₹1,00,000.',
            'unlocked': False
        })

    # Badge 4: Goal Striker (Completed 1+ Goals)
    completed_goals = [g for g in goals if g.completion_percentage >= 100]
    if completed_goals:
        badges.append({
            'title': 'Goal Striker',
            'icon': 'fa-solid fa-bullseye text-danger',
            'description': f'Successfully achieved {len(completed_goals)} target financial goals!',
            'unlocked': True
        })
    else:
        badges.append({
            'title': 'Goal Striker',
            'icon': 'fa-solid fa-bullseye text-muted',
            'description': 'Reach 100% completion on any goal.',
            'unlocked': False
        })

    # Badge 5: AI Pioneer (Recorded 3+ AI auto-tagged expenses)
    ai_expenses = [e for e in expenses if e.auto_classified]
    if len(ai_expenses) >= 3:
        badges.append({
            'title': 'AI Pioneer',
            'icon': 'fa-solid fa-wand-magic-sparkles text-warning',
            'description': 'Used AI auto-classification on 3+ expense entries!',
            'unlocked': True
        })
    else:
        badges.append({
            'title': 'AI Pioneer',
            'icon': 'fa-solid fa-wand-magic-sparkles text-muted',
            'description': 'Use AI expense auto-tagging 3 times.',
            'unlocked': False
        })

    # Monthly Challenges Progress
    unlocked_count = sum(1 for b in badges if b['unlocked'])
    challenge_progress = (unlocked_count / len(badges)) * 100

    return {
        'badges': badges,
        'unlocked_count': unlocked_count,
        'total_badges': len(badges),
        'challenge_progress': round(challenge_progress, 1)
    }
