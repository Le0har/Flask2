from flask import request
from api import ma
from api.models.user import UserModel
from marshmallow import post_load, validate, fields


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        exclude = ('password_hash',)

    name = ma.auto_field(required=True, validate=validate.Length(min=4))
    password = fields.Str(required=True, validate=validate.Length(min=5, max=15))

    @post_load
    def make_user(self, data, **kwargs):
        if request.method == 'POST':
            return UserModel(**data)
        return data

user_schema = UserSchema()
users_schema = UserSchema(many=True)
