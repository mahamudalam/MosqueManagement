from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))

            if current_user.role == "Admin" or current_user.role in allowed_roles:
                return view_func(*args, **kwargs)

            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("dashboard.dashboard"))

        wrapper.__name__ = view_func.__name__
        return wrapper

    return decorator
