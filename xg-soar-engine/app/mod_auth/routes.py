# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from flask_login import login_required, login_user, logout_user, login_required, current_user

# Import password / encryption helper tools
from werkzeug.security import check_password_hash, generate_password_hash

# Import the database object from the main app module
from app import db

# Import module forms
from app.mod_auth.forms import *

# Import module models (i.e. User)
from app.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

@mod_auth.route('/')
@mod_auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):    
                user.authenticated = True
                login_user(user)
                return redirect(url_for('web.dashboard'))

        flash('Incorrect password or email')
        return render_template('mod_auth/login.html', title='Login', form=form, category='danger')
    
    if User.query.all():
        return render_template('mod_auth/login.html', title='Login', form=form)
    else:
        return redirect(url_for('auth.signup'))

    


@mod_auth.route('/signup', methods=['GET','POST'])
def signup():

    form = SignupForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('This email address is already registered', category='danger')
            return render_template('mod_auth/signup.html', title='SignUp', form=form)

        else:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha512')
            new_user = User(email=form.email.data, password=hashed_password, firstname=form.firstname.data,\
                            lastname=form.lastname.data)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Congratulations, log in to get started!', category='success')
            return redirect(url_for('auth.login'))
    
    if User.query.all():
        return redirect(url_for('auth.login'))
        

    return render_template('mod_auth/signup.html', title='SignUp', form=form)
