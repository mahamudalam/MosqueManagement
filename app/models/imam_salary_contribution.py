from app import db


class ImamSalaryContribution(db.Model):
    __tablename__ = "imam_salary_contribution"

    __table_args__ = (
        db.UniqueConstraint(
            "member_id",
            "salary_month",
            "salary_year",
            name="uq_member_salary_month_year"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("member.id", ondelete="CASCADE"),
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

    contribution_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    amount_due = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0.00
    )

    remarks = db.Column(
        db.Text
    )

    member = db.relationship(
        "Member",
        back_populates="imam_salary_contributions"
    )

    def __repr__(self):
        return (
            f"<ImamSalaryContribution("
            f"id={self.id}, "
            f"member_id={self.member_id}, "
            f"month={self.salary_month}, "
            f"year={self.salary_year})>"
        )