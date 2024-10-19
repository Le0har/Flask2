from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

ma = Marshmallow(app)
ma.init_app(app)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer') 
multi_auth = MultiAuth(basic_auth, token_auth) 


@basic_auth.verify_password
def verify_password(username, password):
    from api.models.user import UserModel
    user = db.one_or_404(db.select(UserModel).filter_by(name=username))
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


def verify_token(token):
   from api.models.user import UserModel
   user = UserModel.verify_auth_token(token)
   return user


# Обязательно добавить импорт для обработчиков author, quote, user
from api.handlers import author
from api.handlers import quote
from api.handlers import user
from api.handlers import token
from api.auth.views import auth as bp_auth
app.register_blueprint(bp_auth)