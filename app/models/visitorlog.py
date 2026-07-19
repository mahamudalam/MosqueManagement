from app import db
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class VisitorLog(db.Model):

    __tablename__ = "visitor_logs"

    visitor_id = db.Column(db.Integer, primary_key=True)

    visitor_uuid = db.Column(db.String(100), unique=True, nullable=False)

    ip_address = db.Column(db.String(45))

    user_agent = db.Column(db.Text)

    browser = db.Column(db.String(100))

    operating_system = db.Column(db.String(100))

    device = db.Column(db.String(100))

    first_visit = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(IST)
    )

    last_visit = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(IST)
    )

    visit_count = db.Column(
        db.Integer,
        default=1
    )