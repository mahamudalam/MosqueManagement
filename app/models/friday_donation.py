from app import db


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
    remarks = db.Column(db.String(200))
    member = db.relationship("Member")
