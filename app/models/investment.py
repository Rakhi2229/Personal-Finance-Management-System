from datetime import datetime, date
from app import db


class Investment(db.Model):
    """
    Investment Model tracking user's portfolio across asset classes:
    Mutual Funds, Stocks, Gold, PPF, FD, RD, NPS, Bonds.
    """
    __tablename__ = 'investments'

    TYPES = [
        'Mutual Funds', 'Stocks', 'Gold', 'PPF',
        'FD', 'RD', 'NPS', 'Bonds'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='Mutual Funds')
    amount_invested = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    expected_return_rate = db.Column(db.Float, default=12.0)  # Annual CAGR percentage
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def absolute_return(self):
        """Calculate total profit/loss amount."""
        return self.current_value - self.amount_invested

    @property
    def percentage_return(self):
        """Calculate absolute percentage gain/loss."""
        if self.amount_invested > 0:
            return round(((self.current_value - self.amount_invested) / self.amount_invested) * 100, 2)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.type,
            'amount_invested': self.amount_invested,
            'current_value': self.current_value,
            'expected_return_rate': self.expected_return_rate,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'notes': self.notes,
            'absolute_return': self.absolute_return,
            'percentage_return': self.percentage_return,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Investment {self.title}: Invested {self.amount_invested}, Current {self.current_value}>'
