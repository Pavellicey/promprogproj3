from http.server import HTTPServer, CGIHTTPRequestHandler
from flask import Flask, request, url_for, render_template, redirect
from loginform import LoginForm
from signupform import SignupForm
from addform import AddForm
from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm
import sqlite3
from flask import Flask
import sqlalchemy
from sqlalchemy.orm import Session
import hashlib
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
SqlAlchemyBase = sqlalchemy.orm.declarative_base()
__factory = None
logged_in = False
user = {'id': 0, 'login': None, 'name': None, 'hash_password': None, 'role': None}


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])


@app.route('/')
@app.route('/main')
def main():
    global logged_in
    return render_template('main_page.html', title="Главная",
                           big_image_style=url_for('static', filename='big_image_style.css'),
                           logged=logged_in,
                           img1=url_for('static', filename='data/sunbathe.jpg'),
                           img2=url_for('static', filename='data/books.jpg'),
                           user=user, admin=user['role'] == "admin")


@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    form = LoginForm()
    if form.validate_on_submit():
        login, password = form.data['login'], form.data['password']
        matching = cur.execute(f"""SELECT * FROM Users WHERE login = '{login}'""").fetchall()
        if len(matching) > 0:
            if matching[0][3] == password:
                logged_in = True
                print(matching)
                user['id'], user['login'], user['name'], user['hpass'], user['role'] = matching[0]
                return redirect('/main')
            else:
                return render_template('login.html', title='Авторизация', form=form, wrong_pass=True, logged=logged_in)
    return render_template('login.html', title='Авторизация', form=form, logged=logged_in)


@app.route('/logout/<sure>')
def logout(sure):
    global logged_in, user
    if sure == "True":
        logged_in = False
        user = {'id': 0, 'login': None, 'name': None, 'hash_password': None, 'role': None}
        return redirect('/main')
    return render_template('logout.html', title='Выход', logged=logged_in, user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup(err=False):
    global logged_in
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    form = SignupForm()
    if form.validate_on_submit():
        login, name, password, verify = form.data['login'], form.data['username'], form.data['password'], \
                                        form.data['verifying']
        if password == verify:
            cur.execute(f"""INSERT INTO Users(login, name, hash_password) VALUES ('{login}', '{name}', {password    })""")
            con.commit()
            logged_in = True
            matching = cur.execute(f"""SELECT * FROM Users WHERE login = '{login}'""").fetchall()
            user['id'], user['login'], user['name'], user['hpass'], user['role'] = matching[0]
            print('success', matching[0])
            return redirect("/main")
        else:
            print('pass_wrong')
            return render_template('signup.html', title='Авторизация', form=form, err=True, logged=logged_in)
    print('invalid')
    return render_template('signup.html', title='Авторизация', form=form, logged=logged_in)


@app.route('/book_page/<b_id>')
def book_page(b_id):
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    req = f"""SELECT * FROM Books"""
    if b_id != '0':
        req += f""" WHERE book_id = {b_id}"""
        print(req)
    books = {"books": []}
    for i in cur.execute(req).fetchall():
        books["books"].append({'book_id': i[0], 'book_name': i[1], 'author': i[2], 'genre': i[3],
                               'publication_year': i[4], 'arrival_year': i[5], 'owner_id': i[6]})
    return render_template('book_page.html', books=books, logged=logged_in, oid=user['id'],
                           single=len(books["books"]) == 1, user=user, admin=user['role'] == "admin",
                           big_image_style=url_for('static', filename='big_image_style.css'))


@app.route('/order/<b_id>/<o_id>')
def order(b_id, o_id):
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    cur.execute(f"""UPDATE Books
                SET owner_id = {o_id}
                WHERE book_id = {b_id}""")
    con.commit()
    return redirect('/my_books')


@app.route('/give/<b_id>')
def give(b_id):
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    cur.execute(f"""UPDATE Books
                SET owner_id = 0
                WHERE book_id = {b_id}""")
    con.commit()
    return redirect('/my_books')


@app.route('/my_books')
def my_books():
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    books = {"books": []}
    for i in cur.execute(f"""SELECT * FROM Books WHERE owner_id = {user['id']}""").fetchall():
        books["books"].append({'book_id': i[0], 'book_name': i[1], 'author': i[2], 'genre': i[3],
                               'publication_year': i[4], 'arrival_year': i[5], 'owner_id': i[6]})
    return render_template('your_books.html', books=books, logged=logged_in, user=user)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    form = AddForm()
    if form.validate_on_submit():
        book_name, author, genre, p_year, a_year, o_id = form.data['book_name'], form.data['author'], \
                                                         form.data['genre'], form.data['public_year'], \
                                                         datetime.date.today().year, 0
        cur.execute(f"""INSERT INTO Books(book_name, author, genre, publication_year, arrival_year, owner_id)
        VALUES('{book_name}', '{author}', '{genre}', {p_year}, {a_year}, {o_id})""")
        con.commit()
        return redirect('/book_page/0')
    return render_template('add_book.html', title='Добавление книги', form=form, user=user)


@app.route('/delete_book/<b_id>/<sure>')
def delete_book(b_id, sure):
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    if sure == "True":
        cur.execute(f"""DELETE FROM Books WHERE book_id = {b_id}""")
        con.commit()
        return redirect('/book_page/0')
    b_name = cur.execute(f"""SELECT book_name FROM Books WHERE book_id = {b_id}""").fetchall()
    return render_template('delete_book.html', title='Выход', logged=logged_in, user=user, book_name=b_name[0][0],
                           book_id=b_id)


@app.route('/user_page/<u_id>')
def user_page(u_id):
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    req = f"""SELECT id, login, name, role FROM Users"""
    if u_id != '0':
        req += f""" WHERE id = {u_id}"""
        print(req)
    users = {"users": []}
    for i in cur.execute(req).fetchall():
        users["users"].append({'id': i[0], 'login': i[1], 'name': i[2], 'role': i[3]})
    return render_template('user_page.html', users=users, single=len(users["users"]) == 1, user=user,
                           title="Пользователи", logged=logged_in, admin=user['role'] == 'admin')


@app.route('/ban/<u_id>/<sure>')
def ban(u_id, sure):
    con = sqlite3.connect('static/data/database.db')
    cur = con.cursor()
    if sure == "True":
        cur.execute(f"""UPDATE Users
                SET role = 'banned'
                WHERE id = {u_id}""")
        con.commit()
        return redirect('/user_page/0')
    name = cur.execute(f"""SELECT login FROM Users WHERE id = {u_id}""").fetchall()
    return render_template('ban.html', title='Выход', logged=logged_in, user=user, book_name=name[0][0],
                           uid=u_id)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
    # print(hash('pass'))
