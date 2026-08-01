from datetime import datetime, date
from app import db


class Goal(db.Model):
    """
    Goal Model tracking target financial milestones (Car, House, Retirement, etc.)
    and progress calculations.
    """
    __tablename__ = 'goals'

    CATEGORIES = [
        'Buy Bike', 'Buy Car', 'House', 'Vacation',
        'Higher Education', 'Marriage', 'Retirement', 'Emergency Fund', 'Others'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Others')
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def remaining_amount(self):
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def completion_percentage(self):
        if self.target_amount > 0:
            return min(100.0, round((self.current_amount / self.target_amount) * 100, 1))
        return 0.0

    @property
    def monthly_contribution_needed(self):
        """Calculates monthly savings required to achieve target amount by target date."""
        today = date.today()
        if self.target_date <= today:
            return self.remaining_amount
        months_left = (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month)
        if months_left <= 0:
            months_left = 1
        return round(self.remaining_amount / months_left, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'category': self.category,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'remaining_amount': self.remaining_amount,
            'completion_percentage': self.completion_percentage,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'monthly_contribution_needed': self.monthly_contribution_needed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Goal {self.title}: {self.current_amount}/{self.target_amount}>'
