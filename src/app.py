import json
import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from src.db import init_app as init_db_app
from src.models import db
from werkzeug.exceptions import HTTPException

spec = APISpec(
    title="Flask Blog API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="Flask Blog API with JWT Authentication and Role-Based Access Control"
    ),
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
ma = Marshmallow()


def create_app(environment=None, test_config=None):
    if isinstance(environment, dict) and test_config is None:
        test_config = environment
        environment = None

    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(f"src.config.{environment.capitalize()}Config")

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    init_db_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app=app)
    bcrypt.init_app(app)

    # initialize marshmallow with the app
    ma.init_app(app)

    from src.controllers import auth, post, role, user

    app.register_blueprint(user.app)
    app.register_blueprint(post.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)

    @app.route("/docs")
    def docs():
        return spec.path(view=user.get_user).to_dict()

    @app.errorhandler(HTTPException)
    def handle_exception(e):

        response = e.get_response()

        response.data = json.dumps(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        )

        response.content_type = "application/json"

        return response

    return app
