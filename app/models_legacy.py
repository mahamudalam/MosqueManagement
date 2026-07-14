from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
#from app.models import Member, FridayDonation
from datetime import datetime

# ---------------------
# ADMIN TABLE
# ---------------------
class Admin(UserMixin, db.Model):

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password_hash = db.Column(db.String(255))

    role = db.Column(db.String(30), default="Committee Member")

    status = db.Column(db.String(20), default="Active")

    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Flask-Login loader
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# ---------------------
# MEMBER TABLE
# ---------------------
class Member(db.Model):

    __tablename__ = "member"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    imam_salary_contri = db.Column(db.Float, nullable=False, default=0)
    join_date = db.Column(db.Date)


class FridayDonation(db.Model):
    __tablename__ = "friday_donation"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"))
    donation_date = db.Column(db.Date)
    amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="Due")
    remarks = db.Column(db.String(200))
    member = db.relationship("Member")  

# ---------------------
# Imam contributation
# ---------------------
#from app import db

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
        db.ForeignKey("member.id"),
        nullable=False
    )

    salary_month = db.Column(db.Integer, nullable=False)
    salary_year = db.Column(db.Integer, nullable=False)

    contribution_date = db.Column(db.Date, nullable=False)

    amount = db.Column(db.Float, nullable=False)
    amount_Due = db.Column(db.Float, nullable=False, default=0)

    remarks = db.Column(db.String(200))

    member = db.relationship(
        "Member",
        backref="imam_salary_contributions"
    )

# ---------------------
# Imam Details
# ---------------------
class ImamDetail(db.Model):
    __tablename__ = "imam_details"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20))
    address = db.Column(db.String(200))
    joining_date = db.Column(db.Date)
    monthly_salary = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="Active")


# ---------------------
# Imam Payment Details
# ---------------------

class ImamSalaryPayment(db.Model):
    __tablename__ = "imam_salary_payment"

    id = db.Column(db.Integer, primary_key=True)

    imam_id = db.Column(
        db.Integer,
        db.ForeignKey("imam_details.id"),
        nullable=False
    )

    salary_month = db.Column(db.Integer, nullable=False)
    salary_year = db.Column(db.Integer, nullable=False)

    payment_date = db.Column(db.Date, nullable=False)

    salary_amount = db.Column(db.Float, nullable=False)

    payment_mode = db.Column(db.String(20))
    paid_by = db.Column(db.String(100))
    remarks = db.Column(db.String(200))

    imam = db.relationship("ImamDetail", backref="salary_payments")


# ---------------------
# General Contribution Table
# ---------------------

class GeneralContribution(db.Model):
    __tablename__ = "general_contribution"

    id = db.Column(db.Integer, primary_key=True)

    contributor_name = db.Column(db.String(100), nullable=False)

    contribution_date = db.Column(db.Date, nullable=False)

    amount = db.Column(db.Float, nullable=False)

    payment_mode = db.Column(db.String(20), nullable=False)

    purpose = db.Column(db.String(100))

    received_by = db.Column(db.String(100))

    remarks = db.Column(db.String(200))



    