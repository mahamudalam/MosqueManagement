from datetime import datetime
from app import db


class MonthlyReport(db.Model):
    __tablename__ = "monthly_report"

    report_id = db.Column(db.Integer, primary_key=True)
    report_year = db.Column(db.Integer, nullable=False)
    report_month = db.Column(db.Integer, nullable=False)
    OpeningBalance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    Friday_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    General_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    Imam_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    TotalIncome = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    TotalExpense = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    ClosingBalance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    PDF_Path = db.Column(db.String(500))
    generated_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "report_year",
            "report_month",
            name="uq_monthly_report_year_month",
        ),
    )