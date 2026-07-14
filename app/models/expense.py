from datetime import date
from app import db

class Expense(db.Model):
    __tablename__ = "expense"

    id = db.Column(db.Integer, primary_key=True)

    expense_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(300)
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )
    payment_mode = db.Column(
        db.String(50)
    )

    paid_to = db.Column(
        db.String(150)
    )

    remarks = db.Column(
        db.String(300)
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )