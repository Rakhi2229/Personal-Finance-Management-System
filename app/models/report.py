from datetime import datetime
from app import db


class Report(db.Model):
    """
    Report Model tracking generated PDF / CSV / Excel financial exports.
    """
    __tablename__ = 'reports'

    REPORT_TYPES = [
        'Weekly Report', 'Monthly Report', 'Quarterly Report', 'Yearly Report',
        'Income Report', 'Expense Report', 'Investment Report',
        'Savings Report', 'Budget Report', 'Financial Health Report'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    format = db.Column(db.String(10), default='PDF')  # PDF, CSV, EXCEL
    file_path = db.Column(db.String(255), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'report_type': self.report_type,
            'format': self.format,
            'file_path': self.file_path,
            'generated_at': self.generated_at.strftime('%Y-%m-%d %H:%M:%S') if self.generated_at else None
        }

    def __repr__(self):
        return f'<Report {self.title} ({self.format})>'
