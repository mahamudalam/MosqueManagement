
from app import db
class VisitorCounter(db.Model):
    __tablename__ = "visitor_counter"

    id = db.Column(db.Integer, primary_key=True)
    total_visitors = db.Column(db.Integer, default=0, nullable=False)