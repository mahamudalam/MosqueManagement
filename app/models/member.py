from app import db


class Member(db.Model):
    __tablename__ = "member"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        index=True
    )

    address = db.Column(
        db.Text
    )

    imam_salary_contri = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0.00
    )

    join_date = db.Column(
        db.Date,
        nullable=False
    )

    # Relationships
    friday_donations = db.relationship(
        "FridayDonation",
        back_populates="member",
        cascade="all, delete-orphan",
        lazy=True
    )

    imam_salary_contributions = db.relationship(
    "ImamSalaryContribution",
    back_populates="member",
    cascade="all, delete-orphan",
    lazy=True
    )


    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}')>"