from app import db
from app.models.notification import Notification

def check_and_generate_notifications(user, total_income, total_expense, budgets, goals, savings_rate):
    """
    Evaluates real-time user metrics and triggers intelligent notifications.
    Prevents duplicate unread notifications.
    """
    notifications_created = []

    # Helper to check if similar unread notification exists
    def notification_exists(title_substr):
        return Notification.query.filter(
            Notification.user_id == user.id,
            Notification.is_read == False,
            Notification.title.like(f"%{title_substr}%")
        ).first() is not None

    # Check 1: Budget Breaches
    overall_budget = sum(b.monthly_limit for b in budgets) if budgets else 0
    if overall_budget > 0:
        pct_used = (total_expense / overall_budget) * 100
        if pct_used >= 100 and not notification_exists('Budget Exceeded'):
            n = Notification(
                user_id=user.id,
                title='⚠️ Monthly Budget Exceeded!',
                message=f'Your total spending (₹{total_expense:,.2f}) has crossed your budget limit of ₹{overall_budget:,.2f}.',
                type='danger'
            )
            db.session.add(n)
            notifications_created.append(n)
        elif pct_used >= 85 and pct_used < 100 and not notification_exists('Budget Warning'):
            n = Notification(
                user_id=user.id,
                title='⚠️ Budget Warning (85%+ Used)',
                message=f'You have used {pct_used:.1f}% of your monthly budget. Remaining: ₹{max(0, overall_budget - total_expense):,.2f}.',
                type='warning'
            )
            db.session.add(n)
            notifications_created.append(n)

    # Check 2: Low Savings Rate
    if total_income > 0 and savings_rate < 15 and not notification_exists('Savings Rate Decreased'):
        n = Notification(
            user_id=user.id,
            title='📉 Savings Decreased',
            message=f'Your current savings rate is only {savings_rate:.1f}%. Aim for at least 20% to build wealth.',
            type='warning'
        )
        db.session.add(n)
        notifications_created.append(n)

    # Check 3: Goal Milestones
    for g in goals:
        if g.completion_percentage >= 100 and not notification_exists(f"Goal Completed: {g.title}"):
            n = Notification(
                user_id=user.id,
                title=f'🎯 Goal Achieved: {g.title}!',
                message=f'Congratulations! You reached your target amount of ₹{g.target_amount:,.2f} for {g.title}.',
                type='success'
            )
            db.session.add(n)
            notifications_created.append(n)

    if notifications_created:
        db.session.commit()

    return notifications_created
