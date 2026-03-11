from http import HTTPStatus

from sqlalchemy import func
from src.models import Role, User, db


def test_get_user_success(client, access_token):
    user = db.session.execute(
        db.select(User).where(User.username == "john-wick")
    ).scalar()

    response = client.get(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "user": {
            "id": user.id,
            "username": user.username,
            "role_id": user.role_id,
            "role": {"id": user.role.id, "name": user.role.name},
        }
    }


def test_get_user_not_found(client, access_token):
    user_id = 10

    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user_without_token(client):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_user(client, access_token):

    role_id = db.session.execute(
        db.select(Role.id).where(Role.name == "admin")
    ).scalar()
    payload = {"username": "Bruno", "password": "123456", "role_id": role_id}

    response = client.post(
        "/users/", json=payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "User created!"}
    assert db.session.execute(db.select(func.count(User.id))).scalar() == 2


def test_list_users(client, access_token):

    user = db.session.execute(
        db.select(User).where(User.username == "john-wick")
    ).scalar()

    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json == {
        "identity": str(user.id),
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "role_id": user.role_id,
                "role": {"id": user.role.id, "name": user.role.name},
            },
        ],
    }


def test_list_users_without_token(client):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_user_without_token(client):
    payload = {"username": "Bruno", "password": "123456", "role_id": 1}

    response = client.post("/users/", json=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_user_forbidden_for_non_admin(client, app):
    role_user = Role(name="user")
    db.session.add(role_user)
    db.session.commit()

    user = User(username="maria", role_id=role_user.id)
    user.set_password("123")
    db.session.add(user)
    db.session.commit()

    login_response = client.post(
        "/auth/login",
        json={"username": user.username, "password": "123"},
    )

    token = login_response.json["access_token"]

    payload = {"username": "bruno", "password": "123456", "role_id": role_user.id}

    response = client.post(
        "/users/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json == {"message": "User dosent have access"}


def test_delete_user_success(client, access_token):
    user = db.session.execute(
        db.select(User).where(User.username == "john-wick")
    ).scalar()

    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {"message": "User deleted successfully!"}
    assert db.session.get(User, user.id) is None


def test_delete_user_not_found(client, access_token):
    response = client.delete(
        "/users/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_without_token(client):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_user_forbidden_for_non_admin(client):
    role = Role(name="user")
    db.session.add(role)
    db.session.commit()

    user = User(username="maria", role_id=role.id)
    user.set_password("123")
    db.session.add(user)
    db.session.commit()

    login_response = client.post(
        "/auth/login",
        json={"username": user.username, "password": "123"},
    )
    token = login_response.json["access_token"]

    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json == {"message": "User dosent have access"}


def test_create_user_validation_error(client, access_token):
    payload = {"username": "invalid-user", "role_id": 1}

    response = client.post(
        "/users/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {
        "errors": {"password": ["Missing data for required field."]}
    }


def test_update_user_success(client, access_token):
    user = db.session.execute(
        db.select(User).where(User.username == "john-wick")
    ).scalar()

    payload = {"username": "john-updated"}

    response = client.patch(
        f"/users/{user.id}",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    updated_user = db.session.get(User, user.id)
    assert updated_user.username == "john-wick"


def test_update_user_not_found(client, access_token):
    payload = {"username": "ghost"}

    response = client.patch(
        "/users/999",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Bad username or password"}


def test_login_success(client):
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()

    user = User(username="john-wick", role_id=role.id)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        json={"username": user.username, "password": "test"},
    )

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json


def test_create_user_duplicate_username(client, access_token):
    user = db.session.execute(
        db.select(User).where(User.username == "john-wick")
    ).scalar()

    payload = {
        "username": user.username,
        "password": "newpass",
        "role_id": user.role_id,
    }

    response = client.post(
        "/users/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json == {
        "error": "User not created because username is already in use"
    }
