from flask import Blueprint, render_template, request
from datetime import datetime
from sqlalchemy import extract
from flask_login import login_required

from app.models import FridayDonation, ImamSalaryContribution
from app.routes.access import role_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/friday-report")
#@login_required
#@role_required("Admin", "Committee Member")
def friday_report():
    year = request.args.get("year", datetime.today().year, type=int)
    month = request.args.get("month", datetime.today().month, type=int)

    donations = FridayDonation.query.filter(
        extract("year", FridayDonation.donation_date) == year,
        extract("month", FridayDonation.donation_date) == month
    ).all()

    total_amount = 0
    report_data = []

    for d in donations:
        total_amount += d.amount
        report_data.append({
            "member_name": d.member.name if d.member else "Unknown",
            "amount": d.amount,
            "date": d.donation_date,
            "status": d.status
        })

    return render_template(
        "reports/friday_report.html", 
        report_data=report_data, 
        total_amount=total_amount,
        year=year,
        month=month
    )


@reports_bp.route("/imam-salary-contribution-report")
#@login_required
#@role_required("Admin", "Committee Member")
def imam_salary_contribution_report():
    year = request.args.get("year", datetime.today().year, type=int)
    month = request.args.get("month", datetime.today().month, type=int)

    contributions = ImamSalaryContribution.query.filter(
        ImamSalaryContribution.salary_year == year,
        ImamSalaryContribution.salary_month == month
    ).order_by(ImamSalaryContribution.member_id).all()

    report_data = []
    total_amount = 0

    for c in contributions:
        required_amount = c.member.imam_salary_contri
        actual_amount = c.amount
        due_amount = required_amount - actual_amount

        report_data.append({
            "member_name": c.member.name,
            "amount": c.amount,
            "date": c.contribution_date,
            "salary_month": c.salary_month,
            "salary_year": c.salary_year,
            "remarks": c.remarks,
            "required_amount": required_amount,
            "due_amount": due_amount if due_amount > 0 else 0
        })
        total_amount += c.amount

    return render_template(
        "salary/Imam_salary_contribution_report.html",
        report_data=report_data,
        total_amount=total_amount,
        year=year,
        month=month
    )
