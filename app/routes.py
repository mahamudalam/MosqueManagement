from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Admin, Member, FridayDonation, ImamSalaryContribution, ImamDetail, ImamSalaryPayment,GeneralContribution
from app import db
from datetime import datetime, timedelta
from sqlalchemy import extract,func

main = Blueprint("main", __name__)
# --------------------------
# Helper Function
MONTHS = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
]# --------------------------

def get_fridays(year):
    fridays = []

    current = datetime(year, 1, 1)

    # Find first Friday
    while current.weekday() != 4:
        current += timedelta(days=1)

    # Add every Friday of the year
    while current.year == year:
        fridays.append(current.date())
        current += timedelta(days=7)

    return fridays


# -----------------------
# HOME PAGE
# -----------------------
@main.route("/home")
def home_page():
    return render_template("home.html")


# -----------------------
# ROOT ROUTE
# -----------------------
@main.route("/")
def home():
    return redirect(url_for("main.home_page"))


# -----------------------
# LOGIN
# -----------------------
@main.route("/login", methods=["GET", "POST"])
def login():

    # If already logged in, go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):

            login_user(admin)
            return redirect(url_for("main.dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")


# -----------------------
# DASHBOARD (PROTECTED)
# -----------------------
#@main.route("/dashboard")
#@login_required
#def dashboard():
#    return render_template("dashboard.html")


# -----------------------
# LOGOUT
# -----------------------
@main.route("/logout")
@login_required
def logout():

    logout_user()
    #flash("You have been logged out successfully.", "success")
    return redirect(url_for("main.home_page"))

# -----------------------
# add_member()
# -----------------------
@main.route("/add-member", methods=["GET", "POST"])
@login_required
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

        return redirect(url_for("main.members"))

    return render_template("add_member.html")

@main.route("/members")
@login_required
def members():

    all_members = Member.query.all()
    return render_template("members.html", members=all_members)


@main.route("/edit-member/<int:id>", methods=["GET", "POST"])
@login_required
def edit_member(id):

    member = Member.query.get_or_404(id)

    if request.method == "POST":

        member.name = request.form["name"]
        member.phone = request.form["phone"]
        member.imam_salary_contri = float(request.form["imam_salary_contri"])

        db.session.commit()

        flash("Member updated successfully!")
        return redirect(url_for("main.members"))

    return render_template("edit_member.html", member=member)


@main.route("/delete-member/<int:id>")
@login_required
def delete_member(id):

    member = Member.query.get_or_404(id)

    db.session.delete(member)
    db.session.commit()

    flash("Member deleted successfully!")

    return redirect(url_for("main.members"))

# -----------------------
# friday_donation()
# -----------------------
@main.route("/friday-donation", methods=["GET", "POST"])
@login_required
def friday_donation():

    members = Member.query.order_by(Member.name).all()
    fridays = get_fridays(datetime.today().year)

    if request.method == "POST":

        member_id = request.form["member_id"]

        amount = float(request.form["amount"])

        status = "Paid"
        if amount == 0:
            status = "Due"

        remarks = request.form["remarks"]

        donation_date = datetime.strptime(
            request.form["donation_date"],
            "%Y-%m-%d"
        ).date()

        # Only Friday allowed
        if donation_date.weekday() != 4:

            flash("Only Friday dates are allowed.", "danger")

            donations = FridayDonation.query.order_by(
                FridayDonation.donation_date.desc()
            ).all()

            return render_template(
                "friday_donation.html",
                members=members,
                donations=donations,
                fridays=fridays
            )

        donation = FridayDonation(
            member_id=member_id,
            donation_date=donation_date,
            amount=amount,
            status=status,
            remarks=remarks
        )

        db.session.add(donation)
        db.session.commit()

        flash("Friday donation added successfully.", "success")

        return redirect(url_for("main.friday_donation"))

    donations = FridayDonation.query.order_by(
        FridayDonation.donation_date.desc()
    ).all()

    return render_template(
        "friday_donation.html",
        members=members,
        donations=donations,
        fridays=fridays
    )

# -----------------------
# friday-report
# -----------------------

@main.route("/friday-report")
def friday_report():

    year = request.args.get("year", datetime.today().year, type=int)
    month = request.args.get("month", datetime.today().month, type=int)

    donations = FridayDonation.query.filter(
        extract("year", FridayDonation.donation_date) == year,
        extract("month", FridayDonation.donation_date) == month
    ).all()

    total_amount = 0

    report_data = []

    for d in donations:

        total_amount += d.amount

        report_data.append({
            "member_name": d.member.name if d.member else "Unknown",
            "amount": d.amount,
            "date": d.donation_date,
            "status": d.status
        })

    return render_template(
        "friday_report.html",
        report_data=report_data,
        total_amount=total_amount
    )

# -----------------------
# Imam salary contrubutation
# -----------------------

@main.route("/imam-salary-contribution", methods=["GET", "POST"])
def imam_salary():

    if request.method == "POST":

        member_id = int(request.form["member_id"])
        salary_month = int(request.form["salary_month"])
        salary_year = int(request.form["salary_year"])

        existing = ImamSalaryContribution.query.filter_by(
            member_id=member_id,
            salary_month=salary_month,
            salary_year=salary_year
        ).first()

        if existing:
            flash(
                "This member has already contributed for the selected month.",
                "warning"
            )
            return redirect(url_for("main.imam_salary"))

        contribution = ImamSalaryContribution(
            member_id=member_id,
            salary_month=salary_month,
            salary_year=salary_year,
            contribution_date=datetime.strptime(
                request.form["contribution_date"],
                "%Y-%m-%d"
            ).date(),
            amount=float(request.form["amount"]),
            remarks=request.form.get("remarks")
        )

        db.session.add(contribution)
        db.session.commit()

        flash(
            "Imam salary contribution added successfully.",
            "success"
        )

        return redirect(url_for("main.imam_salary"))

    members = Member.query.order_by(Member.name).all()

    #contributions = ImamSalaryContribution.query.order_by(
    #    ImamSalaryContribution.salary_year.desc(),
    #   ImamSalaryContribution.salary_month.desc(),
    #    ImamSalaryContribution.contribution_date.desc()
    #).all()
    contributions = (
        ImamSalaryContribution.query
        .order_by(ImamSalaryContribution.id.desc())
        .limit(50)
        .all()
    )   

    total_amount = sum(c.amount for c in contributions)

    return render_template(
        "imam_salary_contribution.html",
        members=members,
        contributions=contributions,
        total_amount=total_amount,
        months=MONTHS,
        current_year=datetime.today().year
    )

# -----------------------
# Imam salary contrubutation Report
# -----------------------

@main.route("/imam-salary-contribution-report")
def imam_salary_contribution_report():

    year = request.args.get("year", datetime.today().year, type=int)
    month = request.args.get("month", datetime.today().month, type=int)

    contributions = ImamSalaryContribution.query.filter(
        ImamSalaryContribution.salary_year == year,
        ImamSalaryContribution.salary_month == month
    ).order_by(ImamSalaryContribution.member_id).all()

    report_data = []
    total_amount = 0

    for c in contributions:

        # Calculate due amount
        required_amount = c.member.imam_salary_contri
        actual_amount = c.amount
        due_amount = required_amount - actual_amount

        report_data.append({
            "member_name": c.member.name,
            "amount": c.amount,
            "date": c.contribution_date,
            "salary_month": c.salary_month,
            "salary_year": c.salary_year,
            "remarks": c.remarks,
            "required_amount": required_amount,
            "due_amount": due_amount if due_amount > 0 else 0
        })

        total_amount += c.amount

    return render_template(
        "imam_salary_contribution_report.html",
        report_data=report_data,
        total_amount=total_amount,
        year=year,
        month=month
    )

# -----------------------
# Imam Details
# -----------------------

@main.route("/Imam-Details", methods=["GET", "POST"])
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

        return redirect(url_for("main.Imam_detail"))

    imams = ImamDetail.query.order_by(ImamDetail.id.desc()).limit(20).all()

    return render_template(
        "Add_Imam.html",
        imams=imams
    )


# -----------------------
# Edit Imam
# -----------------------
@main.route("/edit-imam/<int:id>", methods=["GET", "POST"])
@login_required
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
        return redirect(url_for("main.Imam_detail"))

    return render_template("edit_imam.html", imam=imam)


# -----------------------
# Delete Imam
# -----------------------
@main.route("/delete-imam/<int:id>")
@login_required
def delete_imam(id):

    imam = ImamDetail.query.get_or_404(id)

    db.session.delete(imam)
    db.session.commit()

    flash("Imam deleted successfully!", "success")

    return redirect(url_for("main.Imam_detail"))



# -----------------------
# Imam Payment Details
# -----------------------

@main.route("/imam-salary-payment", methods=["GET", "POST"])
def imam_salary_payment():

    if request.method == "POST":

        payment = ImamSalaryPayment(

            imam_id=int(request.form["imam_id"]),
            salary_month=int(request.form["salary_month"]),
            salary_year=int(request.form["salary_year"]),
            payment_date=datetime.strptime(
                request.form["payment_date"],
                "%Y-%m-%d"
            ).date(),

            salary_amount=float(request.form["salary_amount"]),
            payment_mode=request.form["payment_mode"],
            paid_by=request.form["paid_by"],
            remarks=request.form["remarks"]

        )

        db.session.add(payment)
        db.session.commit()

        flash("Imam salary payment saved successfully.", "success")

        return redirect(url_for("main.imam_salary_payment"))

    # Load active Imams for dropdown
    imams = ImamDetail.query.filter_by(
        status="Active"
    ).order_by(
        ImamDetail.name.asc()
    ).all()

    # Show latest 50 salary payments
    payments = ImamSalaryPayment.query.order_by(
        ImamSalaryPayment.payment_date.desc(),
        ImamSalaryPayment.id.desc()
    ).limit(50).all()

    return render_template(
        "imam_salary_payment.html",
        imams=imams,
        payments=payments,
        current_year=datetime.now().year
    )



# -----------------------
# General Contribution 
# -----------------------

@main.route("/general-contribution", methods=["GET", "POST"])
def general_contribution():

    if request.method == "POST":

        contribution = GeneralContribution(

            contributor_name=request.form["contributor_name"],

            contribution_date=datetime.strptime(
                request.form["contribution_date"],
                "%Y-%m-%d"
            ).date(),

            amount=float(request.form["amount"]),

            payment_mode=request.form["payment_mode"],

            purpose=request.form["purpose"],

            received_by=request.form["received_by"],

            remarks=request.form["remarks"]

        )

        db.session.add(contribution)
        db.session.commit()

        flash("General contribution added successfully.", "success")

        return redirect(url_for("main.general_contribution"))

    contributions = GeneralContribution.query.order_by(
        GeneralContribution.id.desc()
    ).limit(50).all()

    return render_template(
        "general_contribution.html",
        contributions=contributions
    )


# -----------------------
# DashBoard Route
# -----------------------

@main.route("/dashboard")
@login_required
def dashboard():

    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # Total Members
    total_members = Member.query.count()

    # Total Imams
    total_imams = ImamDetail.query.count()

    # Friday Donation (Current Month)
    friday_total = db.session.query(
        func.coalesce(func.sum(FridayDonation.amount), 0)
    ).filter(
        FridayDonation.donation_date != None,
        func.strftime('%m', FridayDonation.donation_date) == f"{current_month:02d}",
        func.strftime('%Y', FridayDonation.donation_date) == str(current_year)
    ).scalar()

    # General Contribution (Current Month)
    general_contribution_total = db.session.query(
        func.coalesce(func.sum(GeneralContribution.amount), 0)
    ).filter(
        GeneralContribution.contribution_date != None,
        func.strftime('%m', GeneralContribution.contribution_date) == f"{current_month:02d}",
        func.strftime('%Y', GeneralContribution.contribution_date) == str(current_year)
    ).scalar()

    # Imam Salary Paid (Current Month)
    Imam_salary_contribution_total = db.session.query(
        func.coalesce(func.sum(ImamSalaryContribution.amount), 0)
    ).filter(
        ImamSalaryContribution.salary_month == current_month,
        ImamSalaryContribution.salary_year == current_year
    ).scalar()

    monthly_total = friday_total + general_contribution_total

    return render_template(
        "dashboard.html",
        total_members=total_members,
        total_imams=total_imams,
        friday_total=friday_total,
        Imam_salary_contribution_total=Imam_salary_contribution_total,
        monthly_total=monthly_total,
        general_contribution_total=general_contribution_total
    )