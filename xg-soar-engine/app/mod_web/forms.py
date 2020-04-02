from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, BooleanField
from wtforms.validators import InputRequired, DataRequired, EqualTo, IPAddress, NumberRange, Regexp, URL

class TokenAddForm(FlaskForm):
    token_name = StringField('Token Name', validators=[InputRequired()])
    token_description = StringField('Token Description', validators=[InputRequired()])
    token_expiration = SelectField('Expiration',
        choices=[('1', '1 Days'), ('7', '7 Days'), ('14', '14 Days'), ('30', '30 Days'), ('90', '90 Days'), ('180', '6 Months'), ('365', '1 Year')]
    )

    submit = SubmitField('Save')


class FirewallAddForm(FlaskForm):
    fw_name = StringField('Firewall Name', validators=[InputRequired()])
    username = StringField('Firewall Username', validators=[InputRequired()])
    password = PasswordField('Firewall Password', validators=[InputRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password', message="Passwords do not match")])
    ip_address = StringField('Firewall IP', validators=[InputRequired(), IPAddress()])
    port = IntegerField('Firewall Port', validators=[InputRequired(), NumberRange(min=0, max=65535)])
    initialize = BooleanField('Initialize Now') 


class FirewallEditForm(FlaskForm):
    fw_name = StringField('Firewall Name', validators=[InputRequired()])
    username = StringField('Firewall Username', validators=[InputRequired()])
    ip_address = StringField('Firewall IP', validators=[InputRequired(), IPAddress()])
    port = IntegerField('Firewall Port', validators=[InputRequired(), NumberRange(min=0, max=65535)])


class IpAddForm(FlaskForm):
    ip_address = StringField('IP Address', validators=[InputRequired(), IPAddress()])

class FqdnAddForm(FlaskForm):
    fqdn = StringField('FQDN', validators=[InputRequired(), Regexp('^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$', message='Error not FQDN')])