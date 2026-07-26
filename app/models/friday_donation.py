from app import db
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class ContributionMode(Enum):
    MONEY = "Money"
    RICE = "Rice"
    JUMMA_NAMAZ = "Jumma Namaz"

class FridayDonation(db.Model):
    __tablename__ = "friday_contribution"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"))
    donation_date = db.Column(db.Date)
    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )
    status = db.Column(db.String(20), default="Due")
    contribution_mode = db.Column(
        SQLEnum(
            ContributionMode,
            name="contribution_mode_enum",
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=True
        ),
        nullable=False,
        default=ContributionMode.MONEY
    )
    contribution_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )   
    remarks = db.Column(db.String(200))
    member = db.relationship("Member")
