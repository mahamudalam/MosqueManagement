from functools import wraps
from flask import abort
from flask_login import current_user

from app.permissions import ROLE_PERMISSIONS


def permission_required(permission):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            permissions = ROLE_PERMISSIONS.get(
                current_user.role,
                set()
            )

            if permission not in permissions:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator