from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_required
from datetime import datetime, timedelta,date

from app import db
from app.models import Member, FridayDonation,ContributionMode
#from app.models.friday_donation import FridayDonation, ContributionMode
from app.routes.access import role_required
from zoneinfo import ZoneInfo
from app.services.friday_report_service import (
    FridayReportService
)

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
        remarks = request.form["remarks"]
        contribution_mode = request.form["contribution_mode"]

        if contribution_mode == "Rice" and amount == 0:
            status = "Paid"
        elif contribution_mode == "Money" and amount > 0:
            status = "Paid"
        else:
            status = "Due"

        contribution_date = datetime.strptime(
            request.form["contribution_date"], "%Y-%m-%d"
        ).date()

        selected_fridays = request.form.getlist("donation_date")

        if not selected_fridays:
            flash("Please select at least one Friday.", "warning")
            return redirect(url_for("friday.friday_donation"))

        for friday in selected_fridays:

            friday_date = datetime.strptime(
                friday, "%Y-%m-%d"
            ).date()

            if friday_date.weekday() != 4:
                flash(f"{friday_date} is not a Friday.", "danger")
                return redirect(url_for("friday.friday_donation"))

            existing = FridayDonation.query.filter_by(
                member_id=member_id,
                donation_date=friday_date
            ).first()

            if existing:
                flash(
                    f"Donation already exists for {friday_date.strftime('%d-%b-%Y')}.",
                    "warning"
                )
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

    # =====================================
    # GET: Contribution History
    # =====================================

    selected_contribution_date = request.args.get(
        "contribution_date", ""
    ).strip()

    if selected_contribution_date:

        try:
            filter_date = date.fromisoformat(
                selected_contribution_date
            )

            # Fetch ALL matching records from database
            donations = FridayDonation.query.filter(
                FridayDonation.contribution_date == filter_date
            ).order_by(
                FridayDonation.id.desc()
            ).all()

        except ValueError:
            flash("Invalid contribution date.", "warning")
            selected_contribution_date = ""

            donations = FridayDonation.query.order_by(
                FridayDonation.id.desc()
            ).limit(50).all()

    else:
        # Initial page load and Reset: latest 50 records
        donations = FridayDonation.query.order_by(
            FridayDonation.id.desc()
        ).limit(50).all()

    # Calculate total of displayed records
    total_amount = sum(
        float(d.amount or 0) for d in donations
    )

    return render_template(
        "donation/friday_donation.html",
        members=members,
        donations=donations,
        fridays=fridays,
        today_date=date.today().isoformat(),
        current_month=current_month,
        selected_contribution_date=selected_contribution_date,
        total_amount=total_amount
    )



@friday_bp.route("/get-member-friday-contribution/<int:member_id>")
@login_required
@role_required("Admin", "Committee Member")
def get_member_friday_contribution(member_id):

    member = Member.query.filter_by(id=member_id).first()

    if not member:
        return jsonify({
            "success": False,
            "message": "Member not found"
        }), 404

    selected_year = request.args.get(
        "year", date.today().year, type=int
    )

    service = FridayReportService(
        year=selected_year,
        member_id=member_id
    )

    report = service.generate()

    summary = report.get("member_summary") or {}

    due_dates = summary.get("due_months", [])
    advance_dates = summary.get("advance_months", [])

    return jsonify({
        "success": True,

        "member_name": member.name,

        "total_fridays": summary.get("total_fridays", 0),

        "due_dates": due_dates,
        "due_count": len(due_dates),

        "paid_count": summary.get("paid_friday_count", 0),

        "advance_dates": advance_dates,
        "advance_count": len(advance_dates),

        "advance_amount": str(
            summary.get("advance_amount", 0)
        )
    })

