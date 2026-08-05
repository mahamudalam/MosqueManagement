from datetime import datetime
from app import db


class MonthlyReport(db.Model):
    __tablename__ = "monthly_report"

    report_id = db.Column(db.Integer, primary_key=True)
    report_year = db.Column(db.Integer, nullable=False)
    report_month = db.Column(db.Integer, nullable=False)
    opening_balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    friday_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    friday_money_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    friday_jumma_namaz_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    friday_rice_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    general_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    imam_contribution = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    total_income = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    total_expense = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    closing_balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    pdf_path = db.Column(db.String(500))
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