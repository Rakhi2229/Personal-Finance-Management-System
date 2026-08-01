from datetime import datetime
from app import db


class Budget(db.Model):
    """
    Budget Model for setting category-wise or overall monthly expenditure limits.
    """
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='Overall')
    monthly_limit = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1 to 12
    year = db.Column(db.Integer, nullable=False)   # e.g. 2026
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', 'month', 'year', name='_user_category_month_year_uc'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'monthly_limit': self.monthly_limit,
            'month': self.month,
            'year': self.year,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Budget {self.category} {self.month}/{self.year}: {self.monthly_limit}>'
