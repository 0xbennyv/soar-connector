from flask import Blueprint, redirect, url_for
from app.models import User

mod_default = Blueprint('default', __name__)


@mod_default.route('/', methods=['GET'])
def index():
    if User.query.all():
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.signup'))