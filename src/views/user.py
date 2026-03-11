from marshmallow import fields
from src.app import ma
from src.models import User, db


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing/deserializing ``User`` objects.

    ``SQLAlchemyAutoSchema`` requires a nested :class:`Meta` class that
    points at the model.  The earlier implementation attempted to set
    ``model`` at the top level which left ``table`` unset, causing the
    ``NoneType`` error seen during app startup.

    We also explicitly declare the handful of fields we care about to
    avoid circular imports and to keep control over nested role
    representation.
    """

    class Meta:
        model = User
        sqla_session = db.session
        include_fk = True  # allow role_id to be auto generated


class GetUserParameter(ma.Schema):
    id = fields.Int(required=True, strict=True)


class UserCreateSchema(ma.Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    role_id = fields.Int(required=True, strict=True)
