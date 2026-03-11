from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from src.models import Post, Role, User, db

ma = Marshmallow()


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True


class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True
