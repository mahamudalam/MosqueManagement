from datetime import date, timedelta
from sqlalchemy import extract
from app.models import Member, FridayDonation


class FridayDueReportService:

    def __init__(self, year):
        self.year = year
        self.members = []
        self.lookup = {}
        self.report_data = []
        self.donations = []
        self.summary = {
            "total_members": 0,
            "members_with_due": 0,
            "total_due_fridays": 0
        }

    def load_members(self):
        self.members = (
            Member.query
            .filter(Member.name != "MASJID KHAJANCHI")
            .order_by(Member.name)
            .all()
        )

    def generate(self):

        self.load_members()

        self.load_donations()

        self.build_lookup()

        self.build_report()

        return {
            "report_data": self.report_data,
            "summary": self.summary
        }

    def get_fridays_for_year(self):
        """
        Returns all Friday dates for the selected year.
        """
        fridays = []

        current_day = date(self.year, 1, 1)
        end_day = date(self.year, 12, 31)

        while current_day <= end_day:
            if current_day.weekday() == 4:      # Friday
                fridays.append(current_day)

            current_day += timedelta(days=1)

        return fridays        

    def load_donations(self):
        self.donations = (
            FridayDonation.query
            .filter(
                extract("year", FridayDonation.donation_date) == self.year
            )
            .all()
        )


    def build_lookup(self):

        self.lookup = {}

        for donation in self.donations:

            if donation.member_id not in self.lookup:
                self.lookup[donation.member_id] = set()

            self.lookup[donation.member_id].add(donation.donation_date)        


    def build_report(self):

        self.report_data = []
        self.summary["total_members"] = len(self.members)
        self.summary["members_with_due"] = 0
        self.summary["total_due_fridays"] = 0

        today = date.today()

        all_fridays = self.get_fridays_for_year()

        for member in self.members:

            join_date = member.join_date or date(self.year, 1, 1)

            # Skip members who joined after the selected year
            if join_date.year > self.year:
                continue

            paid_dates = self.lookup.get(member.id, set())

            due_dates = []

            for friday in all_fridays:

                # Ignore Fridays before member joined
                if friday < join_date:
                    continue

                # Ignore future Fridays (only for current year)
                if self.year == today.year and friday > today:
                    continue

                if friday not in paid_dates:
                    due_dates.append(friday)

            if due_dates:

                self.report_data.append({
                    "member_id": member.id,
                    "member_name": member.name,
                    "due_count": len(due_dates),
                    "due_dates": [
                        d.strftime("%d-%b-%Y")
                        for d in due_dates
                    ]
                })

                self.summary["members_with_due"] += 1
                self.summary["total_due_fridays"] += len(due_dates)     