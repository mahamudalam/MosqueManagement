from flask import Blueprint, render_template, request,send_file
from datetime import datetime
from sqlalchemy import extract
from flask_login import login_required

from app.models import FridayDonation, ImamSalaryContribution, MonthlyReport
from app.models.member import Member
from app.routes.access import role_required
import calendar

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.services.report_service import MonthlyReportService
from app.services.imam_salary_contri_report_service import ImamSalaryContributionReportService
from app.services.friday_report_service import FridayReportService

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
    searched = request.args.get("search") == "1"

    if not searched:
        return render_template(
            "reports/friday_report.html",
            searched=False,
            year=datetime.today().year,
            members=Member.query.order_by(Member.name).all()
        )

    service = FridayReportService(
        year=request.args.get("year", type=int),
        month=request.args.get("month", type=int),
        member_id=request.args.get("member_id", type=int),
        status=request.args.get("status")
    )

    data = service.generate()
    data["searched"] = True
    data["members"] = Member.query.order_by(Member.name).all()
    data["member_id"] = request.args.get("member_id", type=int)
    data["year"] = request.args.get("year", type=int) or datetime.today().year
    data["month"] = request.args.get("month", type=int)
    data["status"] = request.args.get("status")

    return render_template(
        "reports/friday_report.html",
        **data
    )


@reports_bp.route("/imam-salary-contribution-report")
# @login_required
# @role_required("Admin", "Committee Member")
def imam_salary_contribution_report():

    
        searched = request.args.get("search") == "1"

        if not searched:

            return render_template(
                "salary/Imam_salary_contribution_report.html",
                searched=False,
                year=datetime.today().year,
                members=Member.query.order_by(Member.name).all()
            )

        service = ImamSalaryContributionReportService(
            year=request.args.get("year", type=int),
            month=request.args.get("month", type=int),
            member_id=request.args.get("member_id", type=int),
            status=request.args.get("status")
        )

        data = service.generate()
        data["searched"] = True

        return render_template(
            "salary/Imam_salary_contribution_report.html",
            **data
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

# ==========================================
# Previous Month Reports 
# ==========================================

@reports_bp.route("/monthly-report")
def monthly_report():

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    report = MonthlyReport.query.filter_by(
        report_year=year,
        report_month=month
    ).first()

    return render_template(
        "partials/monthly_report_card.html",
        report=report,
        month_name=calendar.month_name[month]
    )