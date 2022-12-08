from ast import Num
from email.policy import default
from random import choices
from xml.dom import ValidationErr
from xmlrpc.client import Boolean
from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import StringField,PasswordField,BooleanField,SelectField
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import IntegerField,SearchField,EmailField
import datetime
from wtforms.validators import InputRequired,Length,Email,NumberRange,Email


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name*', validators=[InputRequired(message='First Name Required'), Length(max=15, message='Maximum 15 charachters!')])

    last_name = StringField('Last Name*', validators=[InputRequired(message='Last Name Required'), Length(max=20, message='Maximum 20 characters!')])
# CHECK THIS
    email = EmailField('Email*',validators=[InputRequired(message='Email is Required!'), Email('Please enter valid Email!')])

    username = StringField('Username*',validators=[InputRequired(message='Username Required!'),Length(max=20, message='Username is to long! Maximum length 20 characters!')])

    password = PasswordField('Password*', validators=[InputRequired(message='Password Required!'),Length(min=8, message='Password must be 8 characters or longer!')])

    confirm_password  = PasswordField('Confirm Password', validators=[InputRequired(message='Invalid Password! Try again.')])


# login Form
class LoginForm(FlaskForm):

    username = StringField('Username',validators=[InputRequired(message='Username Required!'),Length(min=1,max=30, message='Please enter Username!')])

    password = PasswordField('Password', validators=[InputRequired(message='Password Required!'),Length(min=8, message='Password must be 8 characters or longer!')])



class DeleteForm(FlaskForm):
    """Delete form -- this form is intentionally blank."""