from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from src.app import User, db


def requires_roles(role_name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            verify_jwt_in_request()

            user_id = int(get_jwt_identity())
            user = db.get_or_404(User, user_id)

            if user.role.name != role_name:
                return {"message": "User dosent have access"}, HTTPStatus.FORBIDDEN

            return f(*args, **kwargs)

        return wrapped

    return decorator
