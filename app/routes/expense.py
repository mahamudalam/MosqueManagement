from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.models import Expense
from app.routes.access import role_required

expense_bp = Blueprint("expense", __name__)


# ==========================================
# Expense List
# ==========================================
@expense_bp.route("/expenses")
@login_required
@role_required("Admin")
def expense_list():

    expenses = Expense.query.order_by(
        Expense.expense_date.desc(),
        Expense.id.desc()
    ).all()

    total_expense = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    return render_template(
        "expense/expense_list.html",
        expenses=expenses,
        total_expense=total_expense
    )


# ==========================================
# Add Expense
# ==========================================
@expense_bp.route("/expense/add", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_expense():

    if request.method == "POST":

        expense = Expense(
            expense_date=datetime.strptime(
                request.form["expense_date"],
                "%Y-%m-%d"
            ).date(),

            category=request.form["category"],
            description=request.form.get("description"),
            amount=float(request.form["amount"]),
            payment_mode=request.form.get("payment_mode"),
            paid_to=request.form.get("paid_to"),
            remarks=request.form.get("remarks")
        )

        db.session.add(expense)
        db.session.commit()

        flash("Expense added successfully.", "success")

        return redirect(url_for("expense.expense_list"))

    return render_template("expense/add_expense.html")


# ==========================================
# Edit Expense
# ==========================================
@expense_bp.route("/expense/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_expense(id):

    expense = Expense.query.get_or_404(id)

    if request.method == "POST":

        expense.expense_date = datetime.strptime(
            request.form["expense_date"],
            "%Y-%m-%d"
        ).date()

        expense.category = request.form["category"]
        expense.description = request.form.get("description")
        expense.amount = float(request.form["amount"])
        expense.payment_mode = request.form.get("payment_mode")
        expense.paid_to = request.form.get("paid_to")
        expense.remarks = request.form.get("remarks")

        db.session.commit()

        flash("Expense updated successfully.", "success")

        return redirect(url_for("expense.expense_list"))

    return render_template(
        "expense/edit_expense.html",
        expense=expense
    )


# ==========================================
# Delete Expense
# ==========================================
@expense_bp.route("/expense/delete/<int:id>")
@login_required
@role_required("Admin")
def delete_expense(id):

    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    flash("Expense deleted successfully.", "success")

    return redirect(url_for("expense.expense_list"))