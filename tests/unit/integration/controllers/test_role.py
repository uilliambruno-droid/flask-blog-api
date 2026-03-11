from http import HTTPStatus

from src.models import Role, User, db
from src.utils import requires_roles


def test_requires_role_success(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "admin"

    mocker.patch("src.utils.verify_jwt_in_request")
    mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(lambda: "success")

    # When
    result = decorated_function()

    # Then
    assert result == "success"


def test_create_role_without_token(client):
    payload = {"name": "manager"}

    response = client.post("/roles/", json=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_create_role_success(client, access_token):
    payload = {"name": "manager"}

    response = client.post(
        "/roles/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "Role created!"}


def test_create_role_forbidden(client):
    role = Role(name="user")
    db.session.add(role)
    db.session.commit()

    user = User(username="maria", password="123", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    login_response = client.post(
        "/auth/login",
        json={"username": user.username, "password": user.password},
    )

    token = login_response.json["access_token"]

    payload = {"name": "manager"}

    response = client.post(
        "/roles/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_role_duplicate(client, access_token):
    role = Role(name="manager")
    db.session.add(role)
    db.session.commit()

    payload = {"name": "manager"}

    response = client.post(
        "/roles/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json == {"error": "Role name already exists"}


def test_requires_role_fail(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "normal"

    mocker.patch("src.utils.verify_jwt_in_request")
    mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(lambda: "success")

    # When
    result = decorated_function()

    # Then
    assert result == (
        {"message": "User dosent have access"},
        HTTPStatus.FORBIDDEN,
    )
