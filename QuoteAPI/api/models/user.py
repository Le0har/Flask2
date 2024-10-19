from passlib.apps import custom_app_context as pwd_context
from api import db
from config import Config
import sqlalchemy.orm as so
import sqlalchemy as sa
from itsdangerous import URLSafeSerializer
from itsdangerous import BadSignature


class UserModel(db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(128))
    

    def __init__(self, name, password):
        self.name = name
        self.hash_password(password)


    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)


    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    

    def generate_auth_token(self):
        s = URLSafeSerializer(Config.SECRET_KEY)
        return s.dumps({'id': self.id})


@staticmethod
def verify_auth_token(token):
    s = URLSafeSerializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except BadSignature:
        return None  # invalid token
    # user = UserModel.query.get(data['id'])
    user = db.get_or_404(UserModel, data['id'])
    return user

