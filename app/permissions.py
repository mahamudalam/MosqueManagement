# app/permissions.py

ROLE_PERMISSIONS = {

    "Admin": {

        "dashboard",
        "manage_users",
        "manage_members",
        "manage_friday_donation",
        "manage_general_contribution",
        "manage_imam",
        "manage_salary",
        "manage_expense",
        "manage_reports",
        "manage_prayer_time",
        "manage_contact",
        "manage_settings",
    },

    "Committee Member": {

        "dashboard",
        "manage_members",
        "manage_friday_donation",
        "manage_general_contribution",
        "manage_imam",
        "manage_salary",
        "manage_expense",
        "manage_reports",
        "manage_prayer_time",
        "manage_contact",
    },

    "Imam": {
        "dashboard",
        "view_own_salary",
        "view_reports",
        "view_prayer_time",
        "view_profile",
    }
}