from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, Regexp, \
                                ValidationError, url, InputRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 120), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
