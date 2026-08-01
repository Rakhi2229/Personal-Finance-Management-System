from datetime import datetime, date
from app import db


class Expense(db.Model):
    """
    Expense Model to store granular user spending transactions.
    Supports auto-classification tag and payment method recording.
    """
    __tablename__ = 'expenses'

    CATEGORIES = [
        'Food', 'Shopping', 'Travel', 'Medical', 'Education',
        'Rent', 'Fuel', 'Entertainment', 'Electricity', 'Internet',
        'EMI', 'Insurance', 'Taxes', 'Others'
    ]

    PAYMENT_METHODS = [
        'Cash', 'UPI', 'Credit Card', 'Debit Card', 'Net Banking'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Others', index=True)
    payment_method = db.Column(db.String(50), nullable=False, default='UPI')
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.Text, nullable=True)
    auto_classified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'amount': self.amount,
            'category': self.category,
            'payment_method': self.payment_method,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'notes': self.notes,
            'auto_classified': self.auto_classified,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Expense {self.title}: {self.amount}>'
