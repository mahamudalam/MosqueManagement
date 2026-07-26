from app.models.member import Member
from app.models.imam_salary_contribution import ImamSalaryContribution
from decimal import Decimal
from datetime import date

class ImamSalaryContributionReportService:

    def __init__(self, year, month=None, member_id=None, status=None):

        self.year = year
        self.month = month
        self.member_id = member_id
        self.status = status

        self.members = []
        self.contributions = []
        self.contribution_lookup = {}

        self.report_data = []
        self.total_amount = Decimal("0.00")

        self.member_summary = None
        self.due_members_summary = None
        self.report_members = []
        self.year_summary = None

    def load_members(self):

        # For dropdown
        self.members = (
        Member.query
        .filter(Member.name != "admin")
        .order_by(Member.name)
        .all()
    )
        #query = Member.query.order_by(Member.id)
       

        #if self.member_id:
         #   query = query.filter(Member.id == self.member_id)

        #self.members = query.all()

        # For report generation
        query = Member.query.filter(
            Member.name != "admin"
        )

        if self.member_id:
            query = query.filter(
                Member.id == self.member_id
            )

        self.report_members = query.order_by(
            Member.name
        ).all()

    def load_contributions(self):

        query = ImamSalaryContribution.query.filter(
            ImamSalaryContribution.salary_year == self.year
        )

        if self.member_id:
            query = query.filter(
                ImamSalaryContribution.member_id == self.member_id
            )

        if self.month:
            query = query.filter(
                ImamSalaryContribution.salary_month == self.month
            )

        self.contributions = query.all()

    def build_lookup(self):

        self.contribution_lookup = {
            (c.member_id, c.salary_month): c
            for c in self.contributions
        }

    def generate(self):

        print("YEAR:", self.year)
        print("MONTH:", self.month)
        print("MEMBER:", self.member_id)

        self.load_members()

        self.load_contributions()

        self.build_lookup()

        self.build_report_data()

        self.build_member_summary()

        self.build_due_members_summary()

        self.build_year_summary()

        return {

            "report_data": self.report_data,

            "total_amount": self.total_amount,

            "member_summary": self.member_summary,

            "due_members_summary": self.due_members_summary,

            "year_summary": self.year_summary,

            "members": self.members,

            "year": self.year,

            "month": self.month,

            "member_id": self.member_id

        }

    def build_member_summary(self):

        if not self.member_id:
            self.member_summary = None
            return

        required_amount = Decimal("0.00")
        paid_amount = Decimal("0.00")
        due_amount = Decimal("0.00")

        paid_months = []
        partial_months = []
        due_months = []

        month_names = [
            "",
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        member_name = ""
        current_date = date.today()
        advance_amount = Decimal("0.00")
        advance_months = []

        for row in self.report_data:

            member_name = row["member_name"]

            required_amount += row["required_amount"]
            paid_amount += row["amount"]
            due_amount += row["due_amount"]

            if row["status"] == "Paid":
                paid_months.append(month_names[row["salary_month"]])

            elif row["status"] == "Partial":
                partial_months.append(month_names[row["salary_month"]])

            else:
                due_months.append(month_names[row["salary_month"]])

        advance_records = ImamSalaryContribution.query.filter(
                ImamSalaryContribution.member_id == self.member_id
            ).order_by(
                ImamSalaryContribution.salary_year,
                ImamSalaryContribution.salary_month
            ).all()

        for record in advance_records:

            # Future month from today's date
            if (
                record.salary_year > current_date.year
                or (
                    record.salary_year == current_date.year
                    and record.salary_month > current_date.month
                    )
                ):

                advance_amount += Decimal(str(record.amount))

                advance_months.append(
                        f"{month_names[record.salary_month]} {record.salary_year}"
                )

        self.member_summary = {
            "member_name": member_name,
            "required_amount": required_amount,
            "paid_amount": paid_amount,
            "due_amount": due_amount,
            "paid_months": paid_months,
            "partial_months": partial_months,
            "due_months": due_months,
            "advance_amount": advance_amount,
            "advance_months": advance_months
        }

    def build_due_members_summary(self):

        if self.member_id or not self.month:
            self.due_members_summary = None
            return

        total_members = len(self.members)
        paid_members = 0
        partial_members = 0
        due_members = 0

        due_member_list = []

        current_date = date.today()

        month_names = [
            "",
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        advance_member_list = []        

        for row in self.report_data:

            if row["status"] == "Paid":
                paid_members += 1

            elif row["status"] == "Partial":
                partial_members += 1
                due_member_list.append({
                    "member_name": row["member_name"],
                    "due_amount": row["due_amount"]
                })

            else:
                due_members += 1
                due_member_list.append({
                    "member_name": row["member_name"],
                    "due_amount": row["due_amount"]
                })
        for member in self.report_members:

            advance_records = ImamSalaryContribution.query.filter(
                ImamSalaryContribution.member_id == member.id
            ).order_by(
                ImamSalaryContribution.salary_year,
                ImamSalaryContribution.salary_month
            ).all()

            months = []

            for record in advance_records:

                if (
                    record.salary_year > current_date.year
                    or (
                        record.salary_year == current_date.year
                        and record.salary_month > current_date.month
                    )
                ):

                    months.append(
                        f"{month_names[record.salary_month]} {record.salary_year}"
                    )

            if months:

                advance_member_list.append({
                    "member_name": member.name,
                    "advance_months": months
                })                



        self.due_members_summary = {
            "total_members": total_members,
            "paid_members": paid_members,
            "partial_members": partial_members,
            "due_members": due_members,
            "members": due_member_list,
            "advance_members": advance_member_list
        }
    def build_report_data(self):

        self.report_data = []
        self.total_amount = Decimal("0.00")

        current_date = date.today()

        for member in self.report_members:

            required_amount = Decimal(str(member.imam_salary_contri))

            join_date = member.join_date

            # Member joined after selected year
            if join_date.year > self.year:
                continue

            # Determine first month
            if join_date.year == self.year:
                start_month = join_date.month
            else:
                start_month = 1

            # Determine months to display
            if self.month:
                # User selected a specific month.
                # Skip member if they joined after the selected month.
                if join_date.year == self.year and join_date.month > self.month:
                    continue

                months = [self.month]

            else:
                # No month selected -> show the full year (or up to current month)
                if self.year == current_date.year:
                    end_month = current_date.month
                else:
                    end_month = 12

                if start_month > end_month:
                    continue

                months = range(start_month, end_month + 1)

            for month in months:

                contribution = self.contribution_lookup.get((member.id, month))

                if contribution:
                    paid_amount = Decimal(str(contribution.amount))
                    contribution_date = contribution.contribution_date
                    remarks = contribution.remarks or ""
                else:
                    paid_amount = Decimal("0.00")
                    contribution_date = None
                    remarks = ""

                due_amount = required_amount - paid_amount

                if due_amount < 0:
                    due_amount = Decimal("0.00")

                # Status
                if paid_amount == 0:
                    status = "Due"
                elif due_amount == 0:
                    status = "Paid"
                else:
                    status = "Partial"

                # Apply Status Filter
                if self.status and self.status.lower() != status.lower():
                    continue

                self.report_data.append({
                    "member_id": member.id,
                    "member_name": member.name,
                    "salary_month": month,
                    "salary_year": self.year,
                    "required_amount": required_amount,
                    "amount": paid_amount,
                    "due_amount": due_amount,
                    "status": status,
                    "date": contribution_date,
                    "remarks": remarks
                })

                self.total_amount += paid_amount
                
    def build_year_summary(self):
        print("BUILD YEAR SUMMARY CALLED")
        print("REPORT MEMBERS COUNT:", len(self.report_members))
        print("CONTRIBUTIONS COUNT:", len(self.contributions))

    # Show only for yearly summary
        if self.month or self.member_id:
            self.year_summary = None
            return


        total_members = len(self.report_members)

        total_required = Decimal("0.00")
        total_paid = Decimal("0.00")
        total_due = Decimal("0.00")


        fully_paid = 0
        partial = 0
        due = 0


        due_members = []


        for member in self.report_members:


            member_required = Decimal(
                str(member.imam_salary_contri)
            )


            member_paid = Decimal("0.00")


            for month in range(1, 13):

                contribution = self.contribution_lookup.get(
                    (member.id, month)
                )


                if contribution:

                    member_paid += Decimal(
                        str(contribution.amount)
                    )


            member_due = (
                member_required * 12
            ) - member_paid


            total_required += (
                member_required * 12
            )

            total_paid += member_paid

            total_due += max(member_due,0)



            if member_due <= 0:

                fully_paid += 1


            elif member_paid > 0:

                partial += 1


            else:

                due += 1



            if member_due > 0:

                due_members.append({

                    "name": member.name,

                    "due_amount": member_due

                })



        self.year_summary = {


            "total_members": total_members,


            "total_required": total_required,


            "total_paid": total_paid,


            "total_due": total_due,


            "fully_paid": fully_paid,


            "partial": partial,


            "due": due,


            "due_members": due_members

                

        }
    