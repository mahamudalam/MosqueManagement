from flask import Blueprint, render_template, request,send_file
from datetime import datetime
from sqlalchemy import extract
from flask_login import login_required

from app.models import FridayDonation, ImamSalaryContribution, MonthlyReport
from app.routes.access import role_required

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.services.report_service import MonthlyReportService

reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


#reports_bp = Blueprint("reports", __name__)


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


# ==========================================
# Monthly Reports 
# ==========================================

@reports_bp.route("/")
@login_required
@role_required("Admin", "Committee Member")
def reports():

    years = list(range(2026, 2036))

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]

    reports = MonthlyReport.query.order_by(
        MonthlyReport.generated_on.desc()
    ).all()

    return render_template(
        "reports/reports.html",
        years=years,
        months=months,
        reports=reports
    )


@reports_bp.route("/generate", methods=["POST"])
@login_required
@role_required("Admin", "Committee Member")
def generate_report():

    year = int(request.form["year"])
    month = int(request.form["month"])

    success, message = MonthlyReportService.generate_monthly_report(year, month)

    if success:
        flash(message, "success")
    else:
        flash(message, "warning")

    return redirect(url_for("reports.reports"))

@reports_bp.route("/view/<int:id>")
@login_required
@role_required("Admin", "Committee Member")
def view_report(id):

    report = MonthlyReport.query.get_or_404(id)

    print(report.PDF_Path)

    return send_file(
        report.PDF_Path,
        mimetype="application/pdf"
    )    

@reports_bp.route("/download/<int:id>")
@login_required
@role_required("Admin", "Committee Member")
def download_report(id):

    report = MonthlyReport.query.get_or_404(id)

    return send_file(
        report.PDF_Path,
        as_attachment=True
    )