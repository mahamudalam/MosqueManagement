from flask import Blueprint, render_template, request, redirect, url_for, flash,make_response
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Admin, PrayerTime
from app.services.visitor_service import track_visitor

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/home")
def home_page():

    visitor_uuid, is_new, total_visitors = track_visitor()
    prayers = PrayerTime.query.order_by(
        PrayerTime.display_order
    ).all()

    response = make_response(
        render_template(
            "auth/home.html",
            prayers=prayers,
            total_visitors=total_visitors
        )
    )

    if is_new:
        response.set_cookie(
            "visitor_uuid",
            visitor_uuid,
            max_age=60 * 60 * 24 * 365,   # 1 year
            httponly=True,
            samesite="Lax"
        )

    return response
    


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