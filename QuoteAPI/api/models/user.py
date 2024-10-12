from passlib.apps import custom_app_context as pwd_context
from api import db
import sqlalchemy.orm as so
import sqlalchemy as sa


class UserModel(db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(128))
    #password: so.Mapped[str] = so.mapped_column(sa.String(128))

    def __init__(self, name, password_hash):
        self.name = name
        self.password_hash = pwd_context.encrypt(password_hash)


    # def hash_password(self, password):
        # self.password_hash = pwd_context.encrypt(password)


    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
