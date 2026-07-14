from app import db

class PrayerTime(db.Model):
    __tablename__ = "prayer_time"

    id = db.Column(db.Integer, primary_key=True)
    prayer_name = db.Column(db.String(20), nullable=False, unique=True)
    prayer_time = db.Column(db.Time, nullable=False)
    display_order = db.Column(db.Integer, nullable=False)