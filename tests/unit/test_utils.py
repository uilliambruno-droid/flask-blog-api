from http import HTTPStatus

from src.app import User
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


def test_requires_role_calls_verify_jwt(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "admin"

    mock_verify = mocker.patch("src.utils.verify_jwt_in_request")
    mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(lambda: "success")

    # When
    decorated_function()

    # Then
    mock_verify.assert_called_once()


def test_requires_role_calls_get_jwt_identity(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "admin"

    mocker.patch("src.utils.verify_jwt_in_request")
    mock_identity = mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(lambda: "success")

    # When
    decorated_function()

    # Then
    mock_identity.assert_called_once()


def test_requires_role_calls_get_or_404_with_user_and_id(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "admin"

    mocker.patch("src.utils.verify_jwt_in_request")
    mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mock_get_or_404 = mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(lambda: "success")

    # When
    decorated_function()

    # Then
    mock_get_or_404.assert_called_once_with(User, 1)


def test_requires_role_fail_does_not_call_wrapped_function(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "normal"

    protected_function = mocker.Mock(return_value="success")

    mocker.patch("src.utils.verify_jwt_in_request")
    mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(protected_function)

    # When
    result = decorated_function()

    # Then
    protected_function.assert_not_called()
    assert result == (
        {"message": "User dosent have access"},
        HTTPStatus.FORBIDDEN,
    )


def test_requires_role_success_calls_wrapped_function(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "admin"

    protected_function = mocker.Mock(return_value="success")

    mocker.patch("src.utils.verify_jwt_in_request")
    mocker.patch("src.utils.get_jwt_identity", return_value="1")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_roles("admin")(protected_function)

    # When
    result = decorated_function()

    # Then
    protected_function.assert_called_once()
    assert result == "success"
