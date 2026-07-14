from app import db


class ImamDetail(db.Model):
    __tablename__ = "imam_details"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    mobile = db.Column(
        db.String(20),
        unique=True,
        index=True
    )

    address = db.Column(
        db.Text
    )

    joining_date = db.Column(
        db.Date,
        nullable=False
    )

    monthly_salary = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0.00
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active",
        index=True
    )

    salary_payments = db.relationship(
        "ImamSalaryPayment",
        back_populates="imam",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<ImamDetail(id={self.id}, name='{self.name}')>"