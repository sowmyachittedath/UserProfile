from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from wtforms import Form, validators, TextField, PasswordField, BooleanField
from UserAPI import *


class Users(db.Model):
    UserID = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    passwd = db.Column(db.String(255), nullable=False)
    emailid = db.Column(db.String(255),unique=True, nullable=False)
    phonenumber = db.Column(db.Integer, nullable=False)

    def set_hash(self,passwd):
        self.passwd = generate_password_hash(passwd)

    def check_password(self, password):
        return check_password_hash(self.passwd, password)





class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    phonenumber = TextField('Phone Number', [validators.Length(min=6, max=10)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated June 22, 2021)', [validators.Required()])

