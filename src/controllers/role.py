from http import HTTPStatus

from flask import Blueprint, request
from src.app import Role, db
from src.utils import requires_roles

app = Blueprint("role", __name__, url_prefix="/roles")


def _create_role():
    data = request.json
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()


@app.route("/", methods=["POST"])
@requires_roles("admin")
def create_role():
    _create_role()
    return {"message": "Role created!"}, HTTPStatus.CREATED
