# Import flask dependencies
from flask import render_template, flash, session, redirect, url_for

# Import Flask Login Dependencies
from flask_login import login_required, current_user

# Import blueprint mod_tokens
from app.mod_web import mod_web

# Import module forms
from app.mod_web.forms import TokenAddForm

# Import module models
from app.models import Tokens

@mod_web.route('/tokens', methods=['GET', 'POST'])
@login_required
def tokens():
    # Get the tokenaddform from app.mod_web.forms
    f = TokenAddForm()
    # Query tokens for default view
    q = Tokens.query.all()
    # validate form on submissions
    if f.validate_on_submit():
        # Init Token Class from models.py
        t = Tokens()
        # Run add module
        t.add(name=f.token_name.data, description=f.token_description.data, \
                    user_id=current_user.id, expires=f.token_expiration.data)
        # Flash messages
        flash('Saved', 'success')
        # Return default token view
        return redirect(url_for('web.tokens'))
    # Return default view
    return render_template('mod_web/tokens.html', title='SOAR Connector', tokens=q, form=f)


# Depricated for bootstrap modal
@mod_web.route('/token/add', methods=['GET','POST'])
@login_required
def token_add():
    # Init tokenaddform from app.mod_web.forms
    f = TokenAddForm()
    # Validate on submission
    if f.validate_on_submit():
        # Init Token class from models.py
        q = Tokens()
        # Run the add modules
        q.add(name=f.token_name.data, description=f.token_description.data, \
                    user_id=current_user.id, expires=f.token_expiration.data)
        # Flash Message
        flash('Saved', 'success')
        # Redirect to web token view
        return redirect(url_for('web.tokens'))
    # Return the default view
    return render_template('mod_web/token_add.html', title='SOAR Connector', form=f)


@mod_web.route('/token/delete/<id>', methods=['GET'])
@login_required
def token_delete(id):
    # Init the Tokens class from models.py
    q = Tokens()
    # run the delete modules
    q.delete(id=id)
    # Redirect to the default tokens view
    return redirect(url_for('web.tokens'))


@mod_web.route('/token/expire/<id>', methods=['GET'])
@login_required
def token_expire(id):
    # Init the Tokens class from models.py
    q = Tokens()
    # Run the expire module
    q.expire(id=id)
    # Redirect to the default view
    return redirect(url_for('web.tokens'))

