import pytest
from src.app import create_app
from src.models import Role, User, db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-jwt-secret-key-32chars-minx",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_set_password_hashes_value(app):
    with app.app_context():
        role = Role(name="admin")
        db.session.add(role)
        db.session.commit()

        user = User(username="hash-user", role_id=role.id)
        user.set_password("secret123")

        assert user.password != "secret123"
        assert user.password.startswith("$2")


def test_check_password_accepts_hashed_password(app):
    with app.app_context():
        role = Role(name="admin")
        db.session.add(role)
        db.session.commit()

        user = User(username="bcrypt-user", role_id=role.id)
        user.set_password("secret123")

        assert user.check_password("secret123") is True
        assert user.check_password("wrong-pass") is False


def test_check_password_accepts_legacy_plain_text_password(app):
    with app.app_context():
        role = Role(name="admin")
        db.session.add(role)
        db.session.commit()

        user = User(username="legacy-user", password="plain-pass", role_id=role.id)

        assert user.check_password("plain-pass") is True
        assert user.check_password("other-pass") is False
