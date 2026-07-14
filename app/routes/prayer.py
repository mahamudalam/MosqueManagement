from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

from app import db
from app.models import PrayerTime

prayer_bp = Blueprint("prayer", __name__)


@prayer_bp.route("/prayer-times")
@login_required
def prayer_times():

    prayers = PrayerTime.query.order_by(
        PrayerTime.display_order
    ).all()

    return render_template(
        "prayer_times.html",
        prayers=prayers
    )


@prayer_bp.route("/edit-prayer-time/<int:id>", methods=["GET","POST"])
@login_required
def edit_prayer_time(id):

    prayer = PrayerTime.query.get_or_404(id)

    if request.method == "POST":

        prayer.prayer_time = datetime.strptime(
            request.form["prayer_time"],
            "%H:%M"
        ).time()

        db.session.commit()

        flash("Prayer time updated successfully.","success")

        return redirect(url_for("prayer.prayer_times"))

    return render_template(
        "edit_prayer_time.html",
        prayer=prayer
    )