from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class SignupForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    verifying = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
