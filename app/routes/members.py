from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

from app import db
from app.models import Member
from app.routes.access import role_required

members_bp = Blueprint("members", __name__)


@members_bp.route("/add-member", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        address = request.form["address"]
        imam_salary_contri = float(request.form["imam_salary_contri"])

        member = Member(
            name=name,
            phone=phone,
            address=address,
            imam_salary_contri=imam_salary_contri,
            join_date=datetime.today()
        )
        db.session.add(member)
        db.session.commit()
        flash("Member added successfully!")
        return redirect(url_for("members.members"))

    return render_template("members/add_member.html")


@members_bp.route("/members")
@login_required
@role_required("Admin", "Committee Member")
def members():
    all_members = Member.query.all()
    return render_template("members/members.html", members=all_members)


@members_bp.route("/edit-member/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def edit_member(id):
    member = Member.query.get_or_404(id)

    if request.method == "POST":
        member.name = request.form["name"]
        member.phone = request.form["phone"]
        member.imam_salary_contri = float(request.form["imam_salary_contri"])
        db.session.commit()
        flash("Member updated successfully!")
        return redirect(url_for("members.members"))

    return render_template("members/edit_member.html", member=member)


@members_bp.route("/delete-member/<int:id>")
@login_required
@role_required("Admin", "Committee Member")
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash("Member deleted successfully!")
    return redirect(url_for("members.members"))
