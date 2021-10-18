import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, g, flash, session
import pandas as pd
import functools
import sqlite3
from datetime import datetime
import db
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(__name__)
 
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, './db/db.sqlite3'),
    SECRET_KEY='foo-baa',
))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        if g.user["role"] != "admin":
            return redirect(url_for('main'))
        return view(**kwargs)

    return wrapped_view
 
def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

today = (datetime.now().strftime('%a %d %B'))

@app.route("/", methods=["GET","POST"])
@login_required
def main():
    if request.method == "GET":
        return render_template("index.html",
                                today=today)

    if request.method == "POST":

        student_name = request.form.get("student_name")
        temperature = request.form.get("temperature")
        parent_id = request.form.get("parent_id")
        input_date = request.form.get("input_date")
        modified_by = request.form.get("modified_by") 
        check_date = request.form.get("check_date")

        con = get_db()
        pk = db.insert(con, student_name, temperature, parent_id, input_date, modified_by, check_date)
        results = db.select_all(con)
       
        return render_template("submit.html",
                                results=results,
                                message_after_submit="Thanks for submitting.",
                                today=today)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = "User {username} is already registered."

        print(error)
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password)) 
            )
            db.commit()
            return redirect(url_for('login'))
            print("Register success.")

        flash(error)

    return render_template('auth/register.html') 

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('main'))
            print("login success.")

        flash(error)

    return render_template('auth/login.html')

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route("/admin", methods=["GET","POST"])
@admin_login_required
def admin_page():
    if request.method =="GET":
        con = get_db()
        results = db.select_all(con)
        users = db.select_all_users(con)
        return render_template("admin/admin.html",
                                results=results,
                                users=users,
                                today=today,
                                admin_page=True)

if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=1016) 