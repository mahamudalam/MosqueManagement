from app import db


class ImamSalaryPayment(db.Model):
    __tablename__ = "imam_salary_payment"

    id = db.Column(db.Integer, primary_key=True)

    imam_id = db.Column(
        db.Integer,
        db.ForeignKey("imam_details.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    salary_month = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    salary_year = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    payment_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    salary_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    payment_mode = db.Column(
        db.String(20)
    )

    paid_by = db.Column(
        db.String(100)
    )

    remarks = db.Column(
        db.Text
    )

    imam = db.relationship(
        "ImamDetail",
        back_populates="salary_payments"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "imam_id",
            "salary_month",
            "salary_year",
            name="uq_imam_salary_payment"
        ),
    )

    def __repr__(self):
        return (
            f"<ImamSalaryPayment("
            f"id={self.id}, "
            f"imam_id={self.imam_id}, "
            f"month={self.salary_month}, "
            f"year={self.salary_year})>"
        )