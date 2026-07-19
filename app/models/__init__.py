from app import db, login_manager

from .admin import Admin, load_user
from .member import Member
from .friday_donation import FridayDonation
from .general_contribution import GeneralContribution
from .imam import ImamDetail
from .imam_salary_contribution import ImamSalaryContribution
from .imam_salary_payment import ImamSalaryPayment
from .PrayerTime import PrayerTime 
from .contact import ContactRequest
from .expense import Expense
from .Monthly_Report import MonthlyReport
from .visitor_counter import VisitorCounter
from .visitorlog import VisitorLog

__all__ = [
    "db",
    "login_manager",
    "Admin",
    "load_user",
    "Member",
    "FridayDonation",
    "GeneralContribution",
    "ImamDetail",
    "ImamSalaryContribution",
    "ImamSalaryPayment",
    "PrayerTime", 
    "ContactRequest",
    "Expense",
    "MonthlyReport",
    "VisitorCounter",
    "VisitorLog",
]
