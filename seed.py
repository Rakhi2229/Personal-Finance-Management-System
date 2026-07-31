from datetime import date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.goal import Goal
from app.models.notification import Notification

app = create_app('development')

def seed_database():
    with app.app_context():
        print("[SEED] Resetting database to clean state...")
        db.drop_all()
        db.create_all()

        # 1. Create Clean User (Zero pre-filled expenses/budgets)
        clean_user = User(
            username='user',
            email='user@fintech.com',
            full_name='FinTech User',
            currency='INR',
            risk_tolerance='Moderate',
            monthly_target_savings=0.0
        )
        clean_user.set_password('user123')
        db.session.add(clean_user)

        # 2. Create Demo User (Optional sample data)
        demo_user = User(
            username='demouser',
            email='demo@fintech.com',
            full_name='Rahul Sharma',
            currency='INR',
            risk_tolerance='Moderate',
            monthly_target_savings=25000.0
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()

        print("[OK] Database successfully initialized with clean state!")
        print("   Clean User Username: user")
        print("   Clean User Password: user123")

if __name__ == '__main__':
    seed_database()
