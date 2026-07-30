from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from decimal import Decimal
from app import db
from app.models import Member, ImamSalaryContribution
from app.routes.access import role_required

salary_bp = Blueprint("salary", __name__)

MONTHS = [
    (1, "January"), (2, "February"), (3, "March"), (4, "April"),
    (5, "May"), (6, "June"), (7, "July"), (8, "August"),
    (9, "September"), (10, "October"), (11, "November"), (12, "December"),
]


@salary_bp.route("/imam-salary-contribution", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def imam_salary():
    if request.method == "POST":
        member_id = int(request.form["member_id"])
        salary_month = int(request.form["salary_month"])
        salary_year = int(request.form["salary_year"])
        amount = Decimal(request.form["amount"])

        # Get monthly Imam contribution from Member table

        imam_salary_contri = (
            db.session.query(Member.imam_salary_contri)
            .filter(Member.id == member_id)
            .scalar()
        )

        # Check if record already exists for this month
        existing = ImamSalaryContribution.query.filter_by(
            member_id=member_id,
            salary_month=salary_month,
            salary_year=salary_year
        ).first()

        if existing:

            remaining = imam_salary_contri - existing.amount

            # Already fully paid
            if remaining <= 0:
                flash(
                    f"Imam contribution for {salary_month}-{salary_year} has already been completed.",
                    "warning"
                )
                return redirect(url_for("salary.imam_salary"))

            # User entered more than remaining amount
            if amount > remaining:
                flash(
                    f"Only ₹{remaining} can be paid for this month.",
                    "warning"
                )
                return redirect(url_for("salary.imam_salary"))

            # Update existing record
            existing.amount += amount
            existing.amount_due = imam_salary_contri - existing.amount
            #existing.contribution_date = datetime.strptime(request.form["contribution_date"], "%Y-%m-%d").date()

        else:

            # First payment for this month

            if amount > imam_salary_contri:
                flash(
                    f"Maximum contribution for this month is ₹{imam_salary_contri}.",
                    "warning"
                )
                return redirect(url_for("salary.imam_salary"))

            new_contribution = ImamSalaryContribution(
                member_id=member_id,
                salary_month=salary_month,
                salary_year=salary_year,
                contribution_date=datetime.strptime(request.form["contribution_date"], "%Y-%m-%d").date(),
                amount=amount,
                remarks=request.form.get("remarks"),
                amount_due=imam_salary_contri - amount
            )

            db.session.add(new_contribution)

        db.session.commit()

        flash("Imam contribution saved successfully.", "success")
        return redirect(url_for("salary.imam_salary"))


    members = Member.query.order_by(Member.name).all()
    contributions = ImamSalaryContribution.query.order_by(ImamSalaryContribution.id.desc()).limit(50).all()
    total_amount = sum(c.amount for c in contributions)

    return render_template(
        "salary/Imam_salary_contribution.html",
        members=members,
        contributions=contributions,
        total_amount=total_amount,
        months=MONTHS,
        current_year=datetime.today().year
    )