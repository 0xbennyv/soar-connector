# Import flask dependencies
from flask import render_template, flash, session, redirect, url_for

# Import Flask Login Dependencies
from flask_login import login_required, current_user

# Import blueprint mod_tokens
from app.mod_web import mod_web

# Import module models (i.e. User)
from app.models import BlackListFqdn

# Import Forms
from app.mod_web.forms import FqdnAddForm

@mod_web.route('/fqdnblacklist', methods=['GET', 'POST'])
@login_required
def fqdns_blacklist():
    # Get form from app.mod_web.forms
    f = FqdnAddForm()
    # Query the FQDN database to load in the FQDN default page
    q = BlackListFqdn.query.all()
    # Validate the form submission
    if f.validate_on_submit():
        # Validate to make sure theres no duplicates
        if BlackListFqdn.query.filter_by(fqdn=f.fqdn.data).first():
            # Flash and error
            flash('ERROR: FQDN already on blacklist', 'danger')
            # Display the FQDN blacklist default view
            return render_template('mod_web/fqdns_blacklist.html', title='SOAR Connector', fqdns=q, form=f)
        # Init the Blacklistfqdn module in models.py
        q = BlackListFqdn()
        # Add to the blacklist
        q.add(fqdn=f.fqdn.data)
        # Redirect to the default view
        return redirect(url_for('web.fqdns_blacklist'))
    # Display default view
    return render_template('mod_web/fqdns_blacklist.html', title='SOAR Connector', fqdns=q, form=f)

# Depricated for the bootstrap modal form
@mod_web.route('/fqdnblacklist/add', methods=['GET', 'POST'])
@login_required
def fqdn_blacklist_add():
    # Get the form from app.mod_web.forms
    f = FqdnAddForm()
    # Validate form submission
    if f.validate_on_submit():
        # Query to see if the fqdn already exists
        if BlackListFqdn.query.filter_by(fqdn=f.fqdn.data).first():
            # Flash a message
            flash('FQDN already on blacklist', 'danger')
            # Render the add page again
            return render_template('mod_web/fqdn_blacklist_add.html', title='SOAR Connector', form=f)
        # Init to BlacklistFqdn module form models.py
        q = BlackListFqdn()
        # Run the add function
        q.add(fqdn=f.fqdn.data)
        # Return the default FQDN view
        return redirect(url_for('web.fqdns_blacklist'))
    # Return the add view.
    return render_template('mod_web/fqdn_blacklist_add.html', title='SOAR Connector', form=f)


@mod_web.route('/blacklistfqdn/delete/<id>', methods=['GET'])
@login_required
def fqdn_blacklist_delete(id):
    # Init the blacklistfqdn blacklist in models.py
    q = BlackListFqdn()
    # Run teh delete module
    q.delete(id=id)
    # Redirect to the default blacklistfqdn view
    return redirect(url_for('web.fqdns_blacklist'))

