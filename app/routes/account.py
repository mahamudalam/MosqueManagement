from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

account_bp = Blueprint("account", __name__)


@account_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("account.change_password"))

        # Match new password
        if new_password != confirm_password:
            flash("New password and Confirm password do not match.", "danger")
            return redirect(url_for("account.change_password"))

        # Minimum length
        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "warning")
            return redirect(url_for("account.change_password"))

        # Prevent same password
        if check_password_hash(current_user.password_hash, new_password):
            flash("New password cannot be the same as the current password.", "warning")
            return redirect(url_for("account.change_password"))

        # Update password
        current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()

        flash("Password changed successfully.", "success")

        return redirect(url_for("dashboard.dashboard"))

    return render_template("account/change_password.html")