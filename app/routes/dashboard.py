from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract

from app import db
from app.models import (
    Member,
    ImamDetail,
    FridayDonation,
    GeneralContribution,
    ImamSalaryContribution,
    Admin,
    PrayerTime,
    ImamSalaryPayment,
    Expense,
    MonthlyReport
)
from app.routes.access import role_required

dashboard_bp = Blueprint("dashboard", __name__)

def get_dashboard_data():
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    total_members = Member.query.filter(Member.name != "admin").count()
    total_imams = ImamDetail.query.filter(ImamDetail.status == "Active").count()

    friday_total = (
        db.session.query(func.coalesce(func.sum(FridayDonation.amount), 0))
        .filter(
            FridayDonation.donation_date.is_not(None),
            extract("month", FridayDonation.donation_date) == current_month,
            extract("year", FridayDonation.donation_date) == current_year,
        )
        .scalar()
    )

    general_contribution_total = (
        db.session.query(func.coalesce(func.sum(GeneralContribution.amount), 0))
        .filter(
            GeneralContribution.contribution_date.is_not(None),
            extract("month", GeneralContribution.contribution_date) == current_month,
            extract("year", GeneralContribution.contribution_date) == current_year,
        )
        .scalar()
    )

    imam_salary_contribution_total = (
        db.session.query(func.coalesce(func.sum(ImamSalaryContribution.amount), 0))
        .filter(
            ImamSalaryContribution.salary_month == current_month,
            ImamSalaryContribution.salary_year == current_year,
        )
        .scalar()
    )

    imam_salary_pay = (
        db.session.query(func.coalesce(func.sum(ImamSalaryPayment.salary_amount), 0))
        .filter(
            ImamSalaryPayment.salary_month == current_month,
            ImamSalaryPayment.salary_year == current_year,
        )
        .scalar()
    )

    total_expense = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            extract("month", Expense.expense_date) == current_month,
            extract("year", Expense.expense_date) == current_year,
        )
        .scalar()
    )

    last_month_total_save = (
        db.session.query(MonthlyReport.ClosingBalance)
        .order_by(MonthlyReport.report_id.desc())
        .limit(1)
        .scalar()
    ) or 0

    monthly_expense = total_expense + imam_salary_pay
    monthly_total = (
        friday_total
        + general_contribution_total
        + imam_salary_contribution_total
    )

    return {
        "total_members": total_members,
        "total_imams": total_imams,
        "friday_total": friday_total,
        "Imam_salary_contribution_total": imam_salary_contribution_total,
        "monthly_total": monthly_total,
        "general_contribution_total": general_contribution_total,
        "current_month_year": today.strftime("%B %Y"),
        "monthly_expense": monthly_expense,
        "remaining_balance": (monthly_total + last_month_total_save) - monthly_expense,
    }

@dashboard_bp.route("/dashboard")
@login_required
@role_required("Admin", "Committee Member", "Imam")
def dashboard():
    return render_template(
        "dashboard/dashboard.html",
        **get_dashboard_data()
    )

@dashboard_bp.route("/users")
@login_required
@role_required("Admin")
def users():

    users = Admin.query.order_by(Admin.created_date.desc()).all()
    return render_template("dashboard/users.html", users=users)


@dashboard_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def create_user():

    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        status = request.form["status"]

        existing = Admin.query.filter_by(username=username).first()
        if existing:
            flash("Username already exists", "danger")
            return redirect(url_for("dashboard.create_user"))

        user = Admin(
            fullname=fullname,
            username=username,
            role=role,
            status=status
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("User created successfully.", "success")
        return redirect(url_for("dashboard.users"))

    return render_template("dashboard/create_user.html")

# ==========================================
# Edit/ Delete user
# ==========================================

@dashboard_bp.route("/users/delete/<int:id>", methods=["POST"])
@login_required
def delete_user(id):
    user = Admin.query.get_or_404(id)

    # Prevent deleting yourself
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("dashboard.users"))

    # Prevent deleting default admin
    if user.username.lower() == "admin":
        flash("Default admin user cannot be deleted.", "danger")
        return redirect(url_for("dashboard.users"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for("dashboard.users"))
