from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_required
from flask_login import current_user

from app.models import db
from app.models.contact import ContactRequest


contact_bp = Blueprint("contact",__name__)

@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"].strip()

        mobile = request.form["mobile"].strip()

        suggestion = request.form["suggestion"].strip()

        if not name or not mobile or not suggestion:

            flash(
                "All fields are required.",
                "danger"
            )

            return redirect(
                url_for("contact.contact")
            )

        obj = ContactRequest(

            name=name,

            mobile=mobile,

            suggestion=suggestion

        )

        db.session.add(obj)

        db.session.commit()

        flash(

            "Thank you! Your suggestion has been submitted.",

            "success"

        )

        return redirect(
            url_for("contact.contact")
        )

    return render_template(
        "contact/contact.html"
    )


@contact_bp.route("/admin/contact-requests")
@login_required
def contact_requests():

    if current_user.role != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    search = request.args.get("search", "").strip()

    query = ContactRequest.query

    if search:
        query = query.filter(
            db.or_(
                ContactRequest.name.ilike(f"%{search}%"),
                ContactRequest.mobile.ilike(f"%{search}%")
            )
        )

    requests = query.order_by(
        ContactRequest.created_on.desc()
    ).all()

    return render_template(
        "contact/admin_contact_requests.html",
        requests=requests,
        search=search
    )


@contact_bp.route("/admin/contact-request/delete/<int:id>")
@login_required
def delete_contact_request(id):

    if current_user.role != "Admin":

        flash(
            "Access denied.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    obj = ContactRequest.query.get_or_404(id)

    db.session.delete(obj)

    db.session.commit()

    flash(

        "Request deleted successfully.",

        "success"

    )

    return redirect(

        url_for("contact.contact_requests")

    )

@contact_bp.route("/admin/contact-request/status/<int:id>/<status>")
@login_required
def update_status(id, status):

    if current_user.role != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    contact = ContactRequest.query.get_or_404(id)

    # Allow only valid statuses
    if status not in ["New", "Reviewed", "Closed"]:
        flash("Invalid status.", "danger")
        return redirect(url_for("contact.contact_requests"))

    contact.status = status

    db.session.commit()

    flash("Status updated successfully.", "success")

    return redirect(url_for("contact.contact_requests"))