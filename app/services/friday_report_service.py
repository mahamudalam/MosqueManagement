from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import extract

from app.models import Member, FridayDonation, ContributionMode


class FridayReportService:
    def __init__(self, year, month=None, member_id=None, status=None):
        self.year = year if year is not None else date.today().year
        self.month = month
        self.member_id = member_id
        self.status = status

        self.members = []
        self.report_members = []
        self.donations = []
        self.lookup = {}
        self.report_data = []
        self.total_amount = Decimal("0.00")
        self.member_summary = None
        self.due_members_summary = None
        self.friday_report_data = []

    def is_future_month(self, donation_date):
        current_date = date.today()
        return (
            donation_date.year > current_date.year
            or (
                donation_date.year == current_date.year
                and donation_date.month > current_date.month
            )
        )

    def is_future_date(self, donation_date):
        return donation_date > date.today()

    def get_status(self, amount, contribution_mode):
        if contribution_mode is None:
            return "Due"

        mode_name = (
            contribution_mode.value
            if hasattr(contribution_mode, "value")
            else str(contribution_mode)
        )

        if mode_name == ContributionMode.MONEY.value:
            return "Paid" if Decimal(str(amount)) > 0 else "Due"

        if mode_name == ContributionMode.RICE.value:
            return "Paid" if Decimal(str(amount)) == 0 else "Due"

        return "Due"

    def load_members(self):
        all_members_query = Member.query.filter(Member.name != "admin")
        self.members = all_members_query.order_by(Member.name).all()

        report_query = Member.query.filter(Member.name != "admin")

        if self.member_id:
            report_query = report_query.filter(Member.id == self.member_id)

        self.report_members = report_query.order_by(Member.name).all()

    def load_donations(self):
        query = FridayDonation.query.filter(
            extract("year", FridayDonation.donation_date) == self.year
        )

        if self.member_id:
            query = query.filter(FridayDonation.member_id == self.member_id)

        if self.month:
            query = query.filter(extract("month", FridayDonation.donation_date) == self.month)

        self.donations = query.order_by(FridayDonation.donation_date.asc()).all()

    def build_lookup(self):
        self.lookup = {}

        for donation in self.donations:
            month = donation.donation_date.month
            key = (donation.member_id, month)
            #key = (donation.member_id, donation.donation_date)

            if key not in self.lookup:
                self.lookup[key] = {
                    "amount": Decimal("0.00"),
                    "date": None,
                    "remarks": [],
                    "statuses": [],
                    "contribution_modes": [],
                    "paid_friday_count": 0
                }

            entry = self.lookup[key]
            entry["amount"] += Decimal(str(donation.amount))
            entry["paid_friday_count"] += 1
            #entry["statuses"].append(
            #    self.get_status(donation.amount, donation.contribution_mode)
            #)

            entry["statuses"].append(donation.status)

            mode_name = (
                donation.contribution_mode.value
                if hasattr(donation.contribution_mode, "value")
                else str(donation.contribution_mode)
            )
            entry["contribution_modes"].append(mode_name)

            if entry["date"] is None or donation.donation_date > entry["date"]:
                entry["date"] = donation.donation_date

            if donation.remarks:
                entry["remarks"].append(donation.remarks)

    def build_friday_report_data(self):
        self.friday_report_data = []

        for donation in self.donations:
            self.friday_report_data.append({
                "member_id": donation.member_id,
                "member_name": donation.member.name,
                "date": donation.donation_date,
                "amount": Decimal(str(donation.amount)),
                "remarks": donation.remarks,
                "status": donation.status,   # From DB
                "contribution_mode": (
                    donation.contribution_mode.value
                    if hasattr(donation.contribution_mode, "value")
                    else str(donation.contribution_mode)
                ),
            })

    def generate(self):
        self.load_members()
        self.load_donations()
        self.build_lookup()

        if self.member_id and not self.month:
            # Year + Member
            self.build_friday_report_data()
        else:
            # Existing monthly report
            self.build_report_data()

        self.build_member_summary()
        self.build_due_members_summary()
        #print("Friday Report:", self.friday_report_data)
        return {
            "report_data": self.report_data,
            "total_amount": self.total_amount,
            "friday_report_data": self.friday_report_data,
            "member_summary": self.member_summary,
            "due_members_summary": self.due_members_summary,
            "members": self.members,
            "year": self.year,
            "month": self.month,
            "member_id": self.member_id,
            "status": self.status,
        }


    def build_report_data(self):
        self.report_data = []
        self.total_amount = Decimal("0.00")

        current_date = date.today()

        for member in self.report_members:
            join_date = getattr(member, "join_date", None)

            if join_date is None:
                join_date = date.today()

            if join_date.year > self.year:
                continue

            if self.month:
                if join_date.year == self.year and join_date.month > self.month:
                    continue
                months = [self.month]
            else:
                if self.year == current_date.year:
                    end_month = current_date.month
                else:
                    end_month = 12

                if join_date.year == self.year:
                    start_month = join_date.month
                else:
                    start_month = 1

                if start_month > end_month:
                    continue

                months = list(range(start_month, end_month + 1))

            for month in months:
                key = (member.id, month)
                entry = self.lookup.get(key)

                if entry:
                    amount = entry["amount"]
                    contribution_date = entry["date"]
                    remarks = ", ".join(entry["remarks"])
                    #status = "Paid" if "Paid" in entry["statuses"] else "Due"
                    paid_fridays = len(entry["statuses"])
                    total_fridays = len(self.get_friday_dates_for_month(self.year, month))

                    status = "Paid" if paid_fridays == total_fridays else "Due"
                    contribution_mode_values = [
                        mode for mode in entry.get("contribution_modes", []) if mode
                    ]
                    contribution_mode = contribution_mode_values[0] if contribution_mode_values else None
                else:
                    amount = Decimal("0.00")
                    contribution_date = None
                    remarks = ""
                    status = "Due"
                    contribution_mode = None

                if self.status and self.status.lower() != status.lower():
                    continue

                self.report_data.append({
                    "member_id": member.id,
                    "member_name": member.name,
                    "month": month,
                    "year": self.year,
                    "amount": amount,
                    "status": status,
                    "date": contribution_date,
                    "remarks": remarks,
                    "contribution_mode": contribution_mode,
                })

                '''print(
                    member.name,
                    month,
                    len(entry["statuses"]) if entry else 0,
                    len(self.get_friday_dates_for_month(self.year, month)),
                    status
                )'''

                self.total_amount += amount

    def build_member_summary(self):
        if not self.member_id:
            self.member_summary = None
            return

        paid_months = []
        due_months = []
        paid_dates = []
        money_count = 0
        rice_count = 0
        total_amount = Decimal("0.00")

        for row in self.report_data:
            total_amount += row["amount"]
            if row["status"] == "Paid":
                paid_months.append(self.month_name(row["month"]))
            else:
                due_months.extend(self.get_friday_dates_for_month(self.year, row["month"]))

        member = self.report_members[0] if self.report_members else None
        member_donations = (
            FridayDonation.query.filter(FridayDonation.member_id == self.member_id)
            .filter(extract("year", FridayDonation.donation_date) == self.year)
            .order_by(FridayDonation.donation_date.asc())
            .all()
        )

        total_fridays = 0
        paid_friday_count = 0
        due_friday_count = 0
        advance_friday_count = 0

        if member is not None:
            join_date = getattr(member, "join_date", None) or date(self.year, 1, 1)
            start_date = max(join_date, date(self.year, 1, 1))
            end_date = date(self.year, 12, 31)
            friday_dates = self.get_friday_dates_for_period(start_date, end_date)
            total_fridays = len(friday_dates)

            donation_lookup = {
                donation.donation_date: donation
                for donation in member_donations
                if donation.donation_date is not None
            }

            for friday_date in friday_dates:
                # Ignore future Fridays
                if friday_date > date.today():
                    continue

                donation = donation_lookup.get(friday_date)

                # No donation for a past Friday = Due
                if donation is None:
                    due_friday_count += 1
                    due_months.append(friday_date.strftime("%d-%b-%Y"))
                    continue

                if donation.status == "Paid":
                    paid_friday_count += 1
                else:
                    due_friday_count += 1
                    due_months.append(friday_date.strftime("%d-%b-%Y"))

            for donation in member_donations:

                if self.month and donation.donation_date.month != self.month:
                    continue

                # Include all MONEY donations in the selected year,
                # even if they are for future dates.
                if donation.contribution_mode == ContributionMode.MONEY:
                    total_amount += Decimal(str(donation.amount))

                if self.get_status(donation.amount, donation.contribution_mode) == "Paid":
                    paid_dates.append(donation.donation_date.strftime("%d-%b-%Y"))

                    if donation.contribution_mode == ContributionMode.MONEY:
                        money_count += 1
                    elif donation.contribution_mode == ContributionMode.RICE:
                        rice_count += 1
                else:
                    due_months.append(donation.donation_date.strftime("%d-%b-%Y"))
        advance_months = []
        for donation in member_donations:
            if self.is_future_date(donation.donation_date):
                advance_months.append(
                    donation.donation_date.strftime("%d-%b-%Y")
                )

        self.member_summary = {
            "member_name": member.name if member else "",
            "total_amount": total_amount,
            "paid_months": paid_months,
            "due_months": due_months,
            "paid_dates": paid_dates,
            "money_count": money_count,
            "rice_count": rice_count,
            "advance_months": advance_months,
            "total_fridays": total_fridays,
            "paid_friday_count": paid_friday_count,
            "due_friday_count": due_friday_count,
            "advance_friday_count": advance_friday_count,
        }

    def build_due_members_summary(self):
        if self.member_id:
            self.due_members_summary = None
            return

        paid_members = 0
        due_members = 0
        due_member_list = []
        advance_member_list = []

        for member in self.report_members:
            member_rows = [
                row for row in self.report_data if row["member_id"] == member.id
            ]
            member_paid = any(row["status"] == "Paid" for row in member_rows)

            if member_paid:
                paid_members += 1
            else:
                due_members += 1
                due_months = []
                for row in member_rows:
                    if row["status"] != "Paid":
                        due_months.append(self.month_name(row["month"]))

                due_member_list.append({
                    "member_name": member.name,
                    "due_months": due_months,
                })

            advance_months = []
            for donation in FridayDonation.query.filter(FridayDonation.member_id == member.id).all():
                if self.is_future_month(donation.donation_date):
                    advance_months.append(
                        donation.donation_date.strftime("%d-%b-%Y")
                    )

            if advance_months:
                advance_member_list.append({
                    "member_name": member.name,
                    "advance_months": advance_months,
                })

        self.due_members_summary = {
            "total_members": len(self.report_members),
            "paid_members": paid_members,
            "due_members": due_members,
            "members": due_member_list,
            "advance_members": advance_member_list,
        }

    @staticmethod
    def month_name(month):
        month_names = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]
        return month_names[month - 1] if 1 <= month <= 12 else ""

    @staticmethod
    def get_friday_dates_for_period(start_date, end_date):
        dates = []
        current_day = start_date

        while current_day <= end_date:
            if current_day.weekday() == 4:
                dates.append(current_day)
            current_day += timedelta(days=1)

        return dates

    @staticmethod
    def get_friday_dates_for_month(year, month):
        if not 1 <= month <= 12:
            return []

        dates = []
        current_day = date(year, month, 1)

        while current_day.month == month:
            if current_day.weekday() == 4:
                dates.append(current_day.strftime("%d-%b-%Y"))
            current_day += timedelta(days=1)

        return dates
