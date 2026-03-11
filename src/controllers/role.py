from http import HTTPStatus

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from src.models import Role, db
from src.utils import requires_roles

app = Blueprint("role", __name__, url_prefix="/roles")


def _create_role():
    data = request.json
    role = Role(name=data["name"])
    db.session.add(role)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Role name already exists"}, HTTPStatus.CONFLICT


@app.route("/", methods=["POST"])
@requires_roles("admin")
def create_role():
    result = _create_role()
    if isinstance(result, tuple):  # error case
        return result
    return {"message": "Role created!"}, HTTPStatus.CREATED
