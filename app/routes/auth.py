from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Admin, PrayerTime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/home")
def home_page():

    prayers = PrayerTime.query.order_by(
        PrayerTime.display_order
    ).all()

    return render_template(
        "auth/home.html",
        prayers=prayers
    )


@auth_bp.route("/")
def home():
    return redirect(url_for("auth.home_page"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid Username or Password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.home_page"))