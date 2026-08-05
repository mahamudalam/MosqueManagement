# app/services/report_service.py

from datetime import date, timedelta,datetime
from sqlalchemy import func
from app.services.pdf_service import PDFService
from app.services.pdf_service import PDFService
import os
from flask import current_app
from zoneinfo import ZoneInfo

from app import db
from app.models import (
    MonthlyReport,
    FridayDonation,
    ContributionMode,
    GeneralContribution,
    ImamSalaryContribution,
    Expense
)


class MonthlyReportService:

    @staticmethod
    def get_previous_month():
        """
        Returns:
            report_year,
            report_month,
            first_day,
            last_day,
            previous_year,
            previous_month
        """

        today = date.today()

        # Current report month (previous month)
        if today.month == 1:
            report_year = today.year - 1
            report_month = 12
        else:
            report_year = today.year
            report_month = today.month - 1

        first_day = date(report_year, report_month, 1)

        first_day_current = date(today.year, today.month, 1)
        last_day = first_day_current - timedelta(days=1)

        # Month before report month
        if report_month == 1:
            previous_year = report_year - 1
            previous_month = 12
        else:
            previous_year = report_year
            previous_month = report_month - 1

        return (
            report_year,
            report_month,
            first_day,
            last_day,
            previous_year,
            previous_month
        )

    @staticmethod
    def report_exists(year, month):

        return MonthlyReport.query.filter_by(
            report_year=year,
            report_month=month
        ).first()

    @staticmethod
    def get_opening_balance(previous_year, previous_month):

        previous_report = MonthlyReport.query.filter_by(
            report_year=previous_year,
            report_month=previous_month
        ).first()

        if previous_report:
            return previous_report.closing_balance

        return 0

    @staticmethod
    def calculate_income(from_date, to_date):

        friday_money = db.session.query(
            func.coalesce(func.sum(FridayDonation.amount), 0)
        ).filter(
            FridayDonation.contribution_mode == ContributionMode.MONEY,
            FridayDonation.contribution_date.between(from_date, to_date)
        ).scalar()

        friday_rice = db.session.query(
            func.coalesce(func.sum(FridayDonation.amount), 0)
        ).filter(
            FridayDonation.contribution_mode== ContributionMode.RICE,
            FridayDonation.contribution_date.between(from_date, to_date)
        ).scalar()

        friday_Jumma_Namaz = db.session.query(
            func.coalesce(func.sum(FridayDonation.amount), 0)
        ).filter(
            FridayDonation.contribution_mode == ContributionMode.JUMMA_NAMAZ,
            FridayDonation.contribution_date.between(from_date, to_date)
        ).scalar()

        general = db.session.query(
            func.coalesce(func.sum(GeneralContribution.amount), 0)
        ).filter(
            GeneralContribution.contribution_date.between(from_date, to_date)
        ).scalar()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  

        imam = db.session.query(
            func.coalesce(func.sum(ImamSalaryContribution.amount), 0)
        ).filter(
            ImamSalaryContribution.contribution_date.between(from_date, to_date)
        ).scalar()

        total_income = friday_money + friday_rice + friday_Jumma_Namaz + general + imam

        return friday_money, friday_rice, friday_Jumma_Namaz, general, imam, total_income

    @staticmethod
    def calculate_expense(from_date, to_date):

        expense = db.session.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.expense_date.between(from_date, to_date)
        ).scalar()

        return expense

    @staticmethod
    def generate_monthly_report(report_year, report_month):

        (
            report_year,
            report_month,
            from_date,
            to_date,
            previous_year,
            previous_month
        ) = MonthlyReportService.get_previous_month()

        # Prevent duplicate report generation
        if MonthlyReportService.report_exists(report_year, report_month):
            print("Monthly report already exists")

            return False, "Monthly report already exists."

        opening_balance = MonthlyReportService.get_opening_balance(
            previous_year,
            previous_month
        )

        friday_money, friday_rice, friday_Jumma_Namaz, general, imam, total_income = (
            MonthlyReportService.calculate_income(
                from_date,
                to_date
            )
        )

        total_expense = MonthlyReportService.calculate_expense(
            from_date,
            to_date
        )

        closing_balance = (
            opening_balance
            + total_income
            - total_expense
        )

        report = MonthlyReport(
            report_year=report_year,
            report_month=report_month,
            opening_balance=opening_balance,
            friday_money_contribution=friday_money,
            friday_jumma_namaz_contribution=friday_Jumma_Namaz,
            friday_rice_contribution=friday_rice,
            general_contribution=general,
            imam_contribution=imam,
            total_income=total_income,
            total_expense=total_expense,
            closing_balance=closing_balance,
            generated_on = datetime.now(ZoneInfo("Asia/Kolkata"))
        )

        db.session.add(report)
        db.session.commit()

        # Generate PDF here
        reports_dir = os.path.join(current_app.root_path,"static","reports"
        )
        os.makedirs(reports_dir, exist_ok=True)
        #pdf_path = f"reports/Monthly_Report_{report_year}_{report_month:02d}.pdf"
        pdf_path = os.path.join(reports_dir,f"Monthly_Report_{report_month}_{report_year:02d}.pdf"
        )

        
        # generate_pdf(report, pdf_path)

        
        pdf_path = PDFService.generate_monthly_report(
                report,
                pdf_path
        )

        report.PDF_Path = pdf_path

        db.session.commit()

        db.session.refresh(report)

        return True, "Monthly report generated successfully."