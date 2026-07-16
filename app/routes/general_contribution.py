from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

from app import db
from app.models import GeneralContribution
from app.routes.access import role_required

general_contribution_bp = Blueprint("general_contribution", __name__)


@general_contribution_bp.route("/general-contribution", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Committee Member")
def general_contribution():
    if request.method == "POST":
        contribution = GeneralContribution(
            contributor_name=request.form["contributor_name"],
            contribution_date=datetime.strptime(request.form["contribution_date"], "%Y-%m-%d").date(),
            amount=float(request.form["amount"]),
            payment_mode=request.form["payment_mode"],
            purpose=request.form["purpose"],
            received_by=request.form["received_by"],
            remarks=request.form["remarks"]
        )
        db.session.add(contribution)
        db.session.commit()
        flash("General contribution added successfully.", "success")
        return redirect(url_for("general_contribution.general_contribution"))

    contributions = GeneralContribution.query.order_by(GeneralContribution.id.desc()).limit(50).all()
    return render_template("donation/General_contribution.html", contributions=contributions)
