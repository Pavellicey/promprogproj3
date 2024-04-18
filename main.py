from http.server import HTTPServer, CGIHTTPRequestHandler
from flask import Flask, request, url_for, render_template, redirect
from loginform import LoginForm
from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
import os
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])


@app.route('/')
def main():
    return render_template('main_page.html', title="Главная")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/book_page')
def book_page():
    return render_template('book_page.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
