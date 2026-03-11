from http import HTTPStatus

from src.models import Role, User, db


def test_login_success(client):
    role = Role(name="normal")
    db.session.add(role)
    db.session.commit()

    user = User(username="john-auth", password="test", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        json={"username": user.username, "password": user.password},
    )

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json


def test_login_user_not_found(client):
    response = client.post(
        "/auth/login",
        json={"username": "ghost", "password": "123"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Bad username or password"}


def test_login_wrong_password(client):
    role = Role(name="normal")
    db.session.add(role)
    db.session.commit()

    user = User(username="john-auth", password="correct", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        json={"username": user.username, "password": "wrong"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Bad username or password"}


def test_login_missing_fields(client):
    response = client.post(
        "/auth/login",
        json={"username": "john"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Bad username or password"}
