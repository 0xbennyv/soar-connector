# Import flask dependencies
from flask import render_template, flash, session, redirect, url_for

# Import Flask Login Dependencies
from flask_login import login_required, current_user

# Import blueprint mod_tokens
from app.mod_web import mod_web

# Import module models
from app.models import BlackListIp

# Import Forms
from app.mod_web.forms import IpAddForm

@mod_web.route('/ipblacklist', methods=['GET', 'POST'])
@login_required
def ips_blacklist():
    # Get the IPAddForm from app.mod_web.form
    f = IpAddForm()
    # Query all IP's in the database for rendering on the default view
    q = BlackListIp.query.all()
    # Validate the page on submission
    if f.validate_on_submit():
        # Check to see if the IP address is already in the list
        if BlackListIp.query.filter_by(ip=f.ip_address.data).first():
            # Flash an error
            flash('ERROR: IP already on blacklist', 'danger')
            # Render the defailt IP Blacklist View
            return render_template('mod_web/ips_blacklist.html', title='SOAR Connector', ips=q, form=f)
        # Init the backlistip class from models.py
        q = BlackListIp()
        # Run the add module
        q.add(ip=f.ip_address.data)
        # Redirect to the default view
        return redirect(url_for('web.ips_blacklist'))
    # Render the default view
    return render_template('mod_web/ips_blacklist.html', title='SOAR Connector', ips=q, form=f)


# Depricated for the bootstrap modal form.
@mod_web.route('/ipblacklist/add', methods=['GET', 'POST'])
@login_required
def ip_blacklist_add():
    # Get the IPAddForm from app.mod_web.form
    f = IpAddForm()
    # validate on submit
    if f.validate_on_submit():
        # see if the ip address is already in the database
        if BlackListIp.query.filter_by(ip=f.ip_address.data).first():
            # Flash a message
            flash('IP already on blacklist', 'danger')
            # Render Add form template
            return render_template('mod_web/ip_blacklist_add.html', title='SOAR Connector', form=f)
        # Init the blacklist IP class
        q = BlackListIp()
        # use the add module
        q.add(ip=f.ip_address.data)
        # Default IP View
        return redirect(url_for('web.ips_blacklist'))
    # List default blacklist view
    return render_template('mod_web/ip_blacklist_add.html', title='SOAR Connector', form=f)


@mod_web.route('/blacklistip/delete/<id>', methods=['GET'])
@login_required
def ip_blacklist_delete(id):
    # Init blacklistip class
    q = BlackListIp()
    # Use the Delete module
    q.delete(id=id)
    # redirect to the blacklist view
    return redirect(url_for('web.ips_blacklist'))
    
