from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo


# Форма для регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField(
        'Password', [InputRequired(), EqualTo('confirm', message='Password must match')])
    confirm = PasswordField('Confirm password', [InputRequired()])


# Форма для логина
class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = StringField('Password', [InputRequired()])