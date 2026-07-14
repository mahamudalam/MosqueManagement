from app import db


class GeneralContribution(db.Model):
    __tablename__ = "general_contribution"

    id = db.Column(db.Integer, primary_key=True)

    contributor_name = db.Column(
        db.String(100),
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

    payment_mode = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )

    purpose = db.Column(
        db.String(100),
        index=True
    )

    received_by = db.Column(
        db.String(100),
        index=True
    )

    remarks = db.Column(
        db.Text
    )

    def __repr__(self):
        return (
            f"<GeneralContribution("
            f"id={self.id}, "
            f"contributor='{self.contributor_name}', "
            f"amount={self.amount})>"
        )