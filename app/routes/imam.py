from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

from app import db
from app.models import ImamDetail, ImamSalaryPayment
from app.routes.access import role_required

imam_bp = Blueprint("imam", __name__)


@imam_bp.route("/Imam-Details", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def Imam_detail():
    if request.method == "POST":
        joining_date = request.form.get("joining_date")
        monthly_salary = request.form.get("monthly_salary")

        new_imam = ImamDetail(
            name=request.form.get("name"),
            mobile=request.form.get("mobile"),
            address=request.form.get("address"),
            joining_date=datetime.strptime(joining_date, "%Y-%m-%d").date() if joining_date else None,
            monthly_salary=float(monthly_salary) if monthly_salary else 0,
            status=request.form.get("status")
        )
        db.session.add(new_imam)
        db.session.commit()
        flash("Imam added successfully.", "success")
        return redirect(url_for("imam.Imam_detail"))

    imams = ImamDetail.query.order_by(ImamDetail.id.desc()).limit(20).all()
    return render_template("imam/Add_Imam.html", imams=imams)


@imam_bp.route("/edit-imam/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def edit_imam(id):
    imam = ImamDetail.query.get_or_404(id)

    if request.method == "POST":
        imam.name = request.form.get("name")
        imam.mobile = request.form.get("mobile")
        imam.address = request.form.get("address")

        joining_date = request.form.get("joining_date")
        if joining_date:
            imam.joining_date = datetime.strptime(joining_date, "%Y-%m-%d").date()

        monthly_salary = request.form.get("monthly_salary")
        if monthly_salary:
            imam.monthly_salary = float(monthly_salary)

        imam.status = request.form.get("status")
        db.session.commit()
        flash("Imam updated successfully!", "success")
        return redirect(url_for("imam.Imam_detail"))

    return render_template("imam/edit_imam.html", imam=imam)


@imam_bp.route("/delete-imam/<int:id>")
@login_required
@role_required("Admin", "Committee Member")
def delete_imam(id):
    imam = ImamDetail.query.get_or_404(id)
    db.session.delete(imam)
    db.session.commit()
    flash("Imam deleted successfully!", "success")
    return redirect(url_for("imam.Imam_detail"))


@imam_bp.route("/imam-salary-payment", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def imam_salary_payment():
    if request.method == "POST":
        payment = ImamSalaryPayment(
            imam_id=int(request.form["imam_id"]),
            salary_month=int(request.form["salary_month"]),
            salary_year=int(request.form["salary_year"]),
            payment_date=datetime.strptime(request.form["payment_date"], "%Y-%m-%d").date(),
            salary_amount=float(request.form["salary_amount"]),
            payment_mode=request.form["payment_mode"],
            paid_by=request.form["paid_by"],
            remarks=request.form["remarks"]
        )
        db.session.add(payment)
        db.session.commit()
        flash("Imam salary payment saved successfully.", "success")
        return redirect(url_for("imam.imam_salary_payment"))

    imams = ImamDetail.query.filter_by(status="Active").order_by(ImamDetail.name.asc()).all()
    payments = ImamSalaryPayment.query.order_by(
        ImamSalaryPayment.payment_date.desc(),
        ImamSalaryPayment.id.desc()
    ).limit(50).all()

    return render_template(
        "salary/imam_salary_payment.html",
        imams=imams,
        payments=payments,
        current_year=datetime.now().year
    )
