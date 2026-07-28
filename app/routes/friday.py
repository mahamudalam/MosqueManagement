from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, timedelta

from app import db
from app.models import Member, FridayDonation,ContributionMode
#from app.models.friday_donation import FridayDonation, ContributionMode
from app.routes.access import role_required
from zoneinfo import ZoneInfo

friday_bp = Blueprint("friday", __name__)

current_month = datetime.today().strftime("%Y-%m")
IST = ZoneInfo("Asia/Kolkata")

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
        #status = "Paid" if amount != 0 else "Due"
        remarks = request.form["remarks"]
        #donation_date = datetime.strptime(request.form["donation_date"], "%Y-%m-%d").date()
        
        contribution_mode = request.form["contribution_mode"]
        if contribution_mode == "Rice" and amount == 0:
                status = "Paid"
        elif contribution_mode == "Money" and amount > 0:
                status = "Paid"
        else:
            status = "Due"
        #status = "Paid" if amount == 0 or contribution_mode=="Rice" else "Due"
        contribution_date=datetime.strptime(request.form["contribution_date"], "%Y-%m-%d").date()

        selected_fridays = request.form.getlist("donation_date")

        if not selected_fridays:
            flash("Please select at least one Friday.", "warning")
            return redirect(url_for("friday.friday_donation"))

        for friday in selected_fridays:

            friday_date = datetime.strptime(friday, "%Y-%m-%d").date()

            # Validate Friday
            if friday_date.weekday() != 4:
                flash(f"{friday_date} is not a Friday.", "danger")
                return redirect(url_for("friday.friday_donation"))

            # Check duplicate
            existing = FridayDonation.query.filter_by(
                member_id=member_id,
                donation_date=friday_date
                #contribution_mode=contribution_mode
            ).first()

            if existing:
                flash(
                    f"Donation already exists for {friday_date.strftime('%d-%b-%Y')}.",
                    "warning"
                )
                #continue
                return redirect(url_for("friday.friday_donation"))

            donation = FridayDonation(
                member_id=member_id,
                donation_date=friday_date,
                amount=amount,
                status=status,
                contribution_mode=contribution_mode,
                contribution_date=contribution_date,
                remarks=remarks
            )

            db.session.add(donation)

        db.session.commit()

        flash("Friday contribution(s) added successfully.", "success")
        return redirect(url_for("friday.friday_donation"))
    donations = FridayDonation.query.order_by(FridayDonation.id.desc()).limit(50).all()
    return render_template(
        "donation/friday_donation.html", 
        members=members, 
        donations=donations,
        fridays=fridays, 
        current_month=current_month)
