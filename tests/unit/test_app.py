import os

from flask import Flask
from src.app import Post, Role, User, create_app


def test_create_app_returns_flask_app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-1234567890",
        }
    )

    assert isinstance(app, Flask)


def test_create_app_applies_default_config():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-1234567890",
        }
    )

    assert app.config["SECRET_KEY"] == "dev"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
    assert app.config["JWT_SECRET_KEY"] == "test-secret-key-1234567890"


def test_create_app_overrides_with_test_config():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "jwt-test-secret-1234567890",
        }
    )

    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test-secret"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["JWT_SECRET_KEY"] == "jwt-test-secret-1234567890"


def test_create_app_registers_blueprints():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-1234567890",
        }
    )

    assert "user" in app.blueprints
    assert "post" in app.blueprints
    assert "auth" in app.blueprints
    assert "role" in app.blueprints


def test_create_app_registers_init_db_command():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-1234567890",
        }
    )

    assert "init-db" in app.cli.commands


def test_create_app_creates_instance_path(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "INSTANCE_PATH": str(tmp_path),
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-1234567890",
        }
    )

    # create_app usa app.instance_path do próprio Flask,
    # então aqui garantimos ao menos que a pasta exista
    assert os.path.exists(app.instance_path)


def test_models_are_registered_in_metadata():
    tables = Role.metadata.tables

    assert Role.__tablename__ in tables
    assert User.__tablename__ in tables
    assert Post.__tablename__ in tables
