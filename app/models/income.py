from datetime import datetime, date
from app import db


class Income(db.Model):
    """
    Income Model to track user income transactions across various categories.
    """
    __tablename__ = 'incomes'

    CATEGORIES = [
        'Salary', 'Business', 'Freelancing', 'Bonus',
        'Gift', 'Investment Returns', 'Rental Income', 'Others'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Salary')
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    payment_method = db.Column(db.String(50), default='Bank Transfer')  # Bank Transfer, Cash, Check, UPI
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Income {self.title}: {self.amount}>'
