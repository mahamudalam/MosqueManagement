from app.services.imam_salary_contri_report_service import (
    ImamSalaryContributionReportService
)


class ImamContriDueReportService:

    def __init__(self, year):
        self.year = year

        self.report_data = []

        self.summary = {
            "total_members": 0,
            "members_with_due": 0,
            "total_due_months": 0
        }

    def generate(self):

        # Reuse existing Imam Salary Contribution service
        service = ImamSalaryContributionReportService(
            year=self.year
        )

        data = service.generate()

        # Existing service already calculates:
        # Paid / Partial / Due
        report_data = data["report_data"]

        self.build_report(report_data)

        return {
            "report_data": self.report_data,
            "summary": self.summary
        }

    def build_report(self, report_data):

        self.report_data = []

        member_lookup = {}

        # --------------------------------------------------
        # Group due/partial months member-wise
        # --------------------------------------------------

        for row in report_data:

            # If there is no outstanding amount,
            # this month is fully paid.
            if row["due_amount"] <= 0:
                continue

            member_id = row["member_id"]
            member_name = row["member_name"]

            if member_id not in member_lookup:

                member_lookup[member_id] = {
                    "member_id": member_id,
                    "member_name": member_name,
                    "due_months": []
                }

            member_lookup[member_id]["due_months"].append({
                "month": row["salary_month"],
                "year": row["salary_year"],
                "required_amount": row["required_amount"],
                "paid_amount": row["amount"],
                "due_amount": row["due_amount"],
                "status": row["status"]
            })

        # --------------------------------------------------
        # Month names
        # --------------------------------------------------

        month_names = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        # --------------------------------------------------
        # Build final report data
        # --------------------------------------------------

        for member in member_lookup.values():

            due_months = member["due_months"]

            self.report_data.append({
                "member_id": member["member_id"],
                "member_name": member["member_name"],

                "due_count": len(due_months),

                "due_months": [
                    f"{month_names[item['month']]} "
                    f"{item['year']}"
                    for item in due_months
                ],

                # Keep detailed information available
                # for future PDF/report enhancements.
                "details": due_months
            })

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        self.summary["total_members"] = len(
            set(
                row["member_id"]
                for row in report_data
            )
        )

        self.summary["members_with_due"] = len(
            self.report_data
        )

        self.summary["total_due_months"] = sum(
            item["due_count"]
            for item in self.report_data
        )