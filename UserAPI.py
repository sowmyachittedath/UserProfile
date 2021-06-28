import gc

from flask import Flask, render_template, request, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
import secrets
from models import *
from functools import wraps
from flask import g, redirect, url_for


secret_key = secrets.token_hex(16)
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

dbUrl = 'mysql://userdummy:chinju$123@localhost/userprofile'
app.config['SQLALCHEMY_DATABASE_URI'] = dbUrl
db = SQLAlchemy(app)


@app.route('/login/', methods=["GET","POST"])
def login_page():
    try:
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            user = Users.query.filter_by(name=username).first()
            if user.check_password(password):
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash("Credentials are wrong")
                return render_template("login.html")
        else:
            return render_template("login.html")
    except Exception as e:
        flash(e)
        return render_template("login.html")



@app.route('/dashboard/')
def dashboard():
    if 'logged_in' in session:
        rows_dic=[]
        rows_dic_temp = {}
        column_keys = ['name','emailid','phonenumber']
        rows = Users.query.with_entities(Users.name,Users.emailid,Users.phonenumber)
        for row in rows:
            for col in column_keys:
                rows_dic_temp[col] = getattr(row, col)
            rows_dic.append(rows_dic_temp)
            rows_dic_temp = {}
        return render_template("index.html",userLst = rows_dic)
    else:
        return redirect(url_for('login_page'))


@app.errorhandler(404)
def pagenotfound(e):
    return render_template("404.html")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))
    return wrap


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))

@app.route("/updateUser",methods=["POST"])
def updateUser():
    oldemail = request.form.get("oldemail")
    name = request.form.get("newusername")
    emailid = request.form.get("newemail")
    phonenumber = request.form.get("newphno")
    user = Users.query.filter_by(emailid=oldemail).first()
    user.name = name
    user.email = emailid
    user.phonenumber = phonenumber
    db.session.merge(user)
    db.session.flush()
    db.session.commit()
    msg = "Information updated successfully"
    return render_template("insert.html", msg=msg)

@app.route("/register/",methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = str(form.password.data)
            phonenumber = form.phonenumber.data
            user = Users.query.filter_by(emailid=email).first()
            if user is not None:
                flash("Email is already registered")
                return render_template('register.html', form=form)
            else:
                entry = Users(name=username, passwd=password, emailid=email, phonenumber=phonenumber)
                entry.set_hash(password)
                db.session.add(entry)
                db.session.commit()
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
        else:
            return render_template('register.html', form=form)
    except Exception as e:
        return (str(e))




@app.route("/loadData",methods=["POST"])
def loadData():
    email = request.form.get("email")
    userdet = Users.query.filter_by(emailid=email).first()
    rows_dic=(userdet.name,userdet.emailid,userdet.phonenumber)
    return jsonify(rows_dic)


if __name__=="__main__":
    app.run(debug=True)