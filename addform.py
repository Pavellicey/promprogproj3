from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import datetime


class AddForm(FlaskForm):
    book_name = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Автор книги', validators=[DataRequired()])
    genre = StringField('Жанр книги', validators=[DataRequired()])
    public_year = IntegerField('Год издания', validators=[DataRequired()])
    submit = SubmitField('Добавить')
