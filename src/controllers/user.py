from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from src.models import User, db
from src.utils import requires_roles
from src.views.user import UserCreateSchema

app = Blueprint("user", __name__, url_prefix="/users")


def _create_user():
    # validate incoming payload with creation schema
    create_schema = UserCreateSchema()
    try:
        data = create_schema.load(request.json)
    except ValidationError as e:
        return {"errors": e.messages}, HTTPStatus.UNPROCESSABLE_ENTITY

    user = User(username=data["username"], role_id=data["role_id"])
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {
            "error": "User not created because username is already in use"
        }, HTTPStatus.CONFLICT

    return {"message": "User created!"}, HTTPStatus.CREATED


def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return [
        {
            "id": user.id,
            "username": user.username,
            "role_id": user.role_id,
            "role": {"id": user.role.id, "name": user.role.name},
        }
        for user in users
    ]


@app.route("/", methods=["GET", "POST"])
@jwt_required()
@requires_roles("admin")
def handle_user():

    if request.method == "POST":
        return _create_user()
    else:
        return {"identity": get_jwt_identity(), "users": _list_users()}


@app.route("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    """
    ---
    get:
      description: Get user details by ID
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
          required: true
          description: The ID of the user to retrieve
      responses:
        200:
          description: User details retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      username:
                        type: string
                        example: "john_doe"
                      role_id:
                        type: integer
                        example: 2
                      role:
                        type: object
                        properties:
                          id:
                            type: integer
                            example: 2
                          name:
                            type: string
                            example: "editor"
        404:
          description: User not found
    """
    user = db.get_or_404(User, user_id)
    return jsonify(
        {
            "user": {
                "id": user.id,
                "username": user.username,
                "role_id": user.role_id,
                "role": {"id": user.role.id, "name": user.role.name},
            }
        }
    )


@app.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@requires_roles("admin")
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully!"}, HTTPStatus.OK
