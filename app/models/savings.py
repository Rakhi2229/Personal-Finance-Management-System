from datetime import datetime
from app import db


class Savings(db.Model):
    """
    Savings Model storing pre-aggregated savings history by time period.
    Formula: Savings = Total Income - Total Expenses
    Savings Rate = (Net Savings / Total Income) * 100
    """
    __tablename__ = 'savings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    period_type = db.Column(db.String(20), nullable=False)  # Weekly, Monthly, Quarterly, Yearly
    period_identifier = db.Column(db.String(30), nullable=False)  # e.g., "2026-07", "2026-Q3", "2026-W30", "2026"
    total_income = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    net_savings = db.Column(db.Float, default=0.0)
    savings_rate = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'period_type', 'period_identifier', name='_user_period_uc'),
    )

    def calculate_metrics(self, income, expense):
        """Calculates Net Savings and Savings Rate."""
        self.total_income = float(income or 0.0)
        self.total_expenses = float(expense or 0.0)
        self.net_savings = self.total_income - self.total_expenses
        if self.total_income > 0:
            self.savings_rate = round((self.net_savings / self.total_income) * 100, 2)
        else:
            self.savings_rate = 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period_type': self.period_type,
            'period_identifier': self.period_identifier,
            'total_income': self.total_income,
            'total_expenses': self.total_expenses,
            'net_savings': self.net_savings,
            'savings_rate': self.savings_rate,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f'<Savings {self.period_identifier}: {self.net_savings}>'
