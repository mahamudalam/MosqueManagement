from datetime import datetime, timezone

from app import db


class ContactRequest(db.Model):
    __tablename__ = "contact_request"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    mobile = db.Column(
        db.String(15),
        nullable=False,
        index=True
    )

    suggestion = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="New",
        index=True
    )

    created_on = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    def __repr__(self):
        return f"<ContactRequest(id={self.id}, name='{self.name}')>"