from http.server import HTTPServer, CGIHTTPRequestHandler
from flask import Flask, request, url_for, render_template, redirect
from loginform import LoginForm
from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
import os
import sqlite3
from flask import Flask
import sqlalchemy
from sqlalchemy.orm import Session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
SqlAlchemyBase = sqlalchemy.orm.declarative_base()
__factory = None
logged_in = False
user = dict()


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])


@app.route('/')
@app.route('/main')
def main():
    return render_template('main_page.html', title="Главная",
                           big_image_style=url_for('static', filename='big_image_style.css'),
                           logged=logged_in,
                           img1=url_for('static', filename='data/sunbathe.jpg'),
                           img2=url_for('static', filename='data/books.jpg'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        login, password = form.data['username'], form.data['password']
        matching = cur.execute(f"""SELECT * FROM Users WHERE login = '{login}'""").fetchall()
        if len(matching) > 0:
            if matching[0][0] == password:
                logged_in = True
                user['id'], user['login'], user['hpass'], user['role'] = matching[0]
                return redirect('/main')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/book_page')
def book_page():
    return render_template('book_page.html')


# @app.route('/my_books')
# def my_books():


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
