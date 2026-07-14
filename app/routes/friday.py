from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, timedelta

from app import db
from app.models import Member, FridayDonation
from app.routes.access import role_required

friday_bp = Blueprint("friday", __name__)

MONTHS = [
    (1, "January"), (2, "February"), (3, "March"), (4, "April"),
    (5, "May"), (6, "June"), (7, "July"), (8, "August"),
    (9, "September"), (10, "October"), (11, "November"), (12, "December"),
]


def get_fridays(year):
    fridays = []
    current = datetime(year, 1, 1)
    while current.weekday() != 4:
        current += timedelta(days=1)
    while current.year == year:
        fridays.append(current.date())
        current += timedelta(days=7)
    return fridays


@friday_bp.route("/friday-donation", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def friday_donation():
    members = Member.query.order_by(Member.name).all()
    fridays = get_fridays(datetime.today().year)

    if request.method == "POST":
        member_id = request.form["member_id"]
        amount = float(request.form["amount"])
        status = "Paid" if amount != 0 else "Due"
        remarks = request.form["remarks"]
        donation_date = datetime.strptime(request.form["donation_date"], "%Y-%m-%d").date()

        if donation_date.weekday() != 4:
            flash("Only Friday dates are allowed.", "danger")
            donations = FridayDonation.query.order_by(FridayDonation.donation_date.desc()).all()
            return render_template("donation/friday_donation.html", members=members, donations=donations, fridays=fridays)

        donation = FridayDonation(
            member_id=member_id,
            donation_date=donation_date,
            amount=amount,
            status=status,
            remarks=remarks
        )
        db.session.add(donation)
        db.session.commit()
        flash("Friday donation added successfully.", "success")
        return redirect(url_for("friday.friday_donation"))

    donations = FridayDonation.query.order_by(FridayDonation.donation_date.desc()).all()
    return render_template("donation/friday_donation.html", members=members, donations=donations, fridays=fridays)
