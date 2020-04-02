# Import Base App Dependencies
from app import db

# Import flask dependencies
from flask import render_template, flash, session, redirect, url_for

# Import Flask Login Dependencies
from flask_login import login_required, current_user

# Import blueprint mod_tokens
from app.mod_web import mod_web

# Import forms used
from app.mod_web.forms import FirewallAddForm, FirewallEditForm

# Import module models
from app.models import Firewalls

# Import Tasks for initialization
from app.mod_tasks import FirewallInitialize, FirewallChecks

@mod_web.route('/firewalls', methods=['GET'])
@login_required
def firewalls():
    # Query all the firewalls in the database
    f = Firewalls.query.all()
    # Render Template and pass the dict to the template
    return render_template('mod_web/firewalls.html', title='SOAR Connector', firewalls=f)


@mod_web.route('/firewall/add/', methods=['GET','POST'])
@login_required
def firewall_add():
    # Firewall form from app.mod_web.forms
    f = FirewallAddForm()
    # Validate the submission
    if f.validate_on_submit():
        # Validate Name
        if Firewalls.query.filter_by(fwname=f.fw_name.data).first():
            flash('Firewall name already in use', 'danger')
            return render_template('mod_web/firewall_add.html', title='SOAR Connector', form=f)
        # Validate if IP is in use already
        if Firewalls.query.filter_by(ip=f.ip_address.data).first():
            flash('IP already in use', 'danger')
            return render_template('mod_web/firewall_add.html', title='SOAR Connector', form=f)
        # Init the Firewalls class in models.py
        q = Firewalls()
        # If we want instant initialization run this
        if f.initialize.data:
            # Run the "add" module in Firewall class
            q.add(fwname=f.fw_name.data, username=f.username.data, password=f.password.data,\
                        ip=f.ip_address.data, port=f.port.data, init=1)
        # Otherwise it'll go in the queue
        else:
            q.add(fwname=f.fw_name.data, username=f.username.data, password=f.password.data,\
                        ip=f.ip_address.data, port=f.port.data, init=0)
        # If post is sucessful redirect to the main firewalls page for status ipdates
        return redirect(url_for('web.firewalls'))
    # Default Page for adding firewalls
    return render_template('mod_web/firewall_add.html', title='SOAR Connector', form=f)


@mod_web.route('/firewall/edit/<id>', methods=['GET','POST'])
@login_required
def firewall_edit(id):
    # Render the firewall edit form
    f = FirewallEditForm()
    # Validate on submission
    if f.validate_on_submit():

        # if Firewalls.query.filter_by(fwname=f.fw_name.data).first():
        #     flash('ERROR: Firewall name already in use', category='danger')
        #     return render_template('mod_web/firewall_edit.html', title='SOAR Connector', form=f)

        # if Firewalls.query.filter_by(ip=f.ip_address.data).first():
        #     flash('ERROR: IP already in use', 'danger')
        #     return render_template('mod_web/firewall_edit.html', title='SOAR Connector', form=f)
        # Init the Firewall Class in models.py
        q = Firewalls()
        # Run the update modules to update the information
        q.update(id=id, fwname=f.fw_name.data, username=f.username.data, \
                ip=f.ip_address.data, port=f.port.data)
        # Flash message notifying of sucess
        flash('Firewall updated', 'success')
        # Redirect to the default firewall page
        return redirect(url_for('web.firewalls'))
    # Run a query for the id to be edited to fill out the form fields
    fw = Firewalls.query.filter_by(id=id).first()
    # Render the template and send the form and firewall query
    return render_template('mod_web/firewall_edit.html', title='SOAR Connector', form=f, fw=fw)


@mod_web.route('/firewall/delete/<id>', methods=['GET'])
@login_required
def firewall_delete(id):
    # Init the Firewall class
    q = Firewalls()
    # Use the delete module
    q.delete(id=id)
    # Redirect to the default firewall page
    return redirect(url_for('web.firewalls'))


@mod_web.route('/firewall/decomission/<id>', methods=['GET'])
@login_required
def firewall_decomission(id):
    # Init the Firewall class
    q = Firewalls()
    # Run the decommission module to start the decommision process
    q.decommision(id=id)
    # Redirect to the default firewall page
    return redirect(url_for('web.firewalls'))


@mod_web.route('/firewall/check/<id>', methods=['GET'])
@login_required
def firewall_auth_check(id):
    # This needs to be re-written into models.py
    f = Firewalls().query.filter_by(id=id).all()
    fw = FirewallChecks(f)
    fw.auth_check()
    flash('Health Check Started - Refresh for update', 'success')
    return redirect(url_for('web.firewalls'))


@mod_web.route('/firewall/reinit/<id>', methods=['GET'])
@login_required
def firewall_reinit(id):
    # Init the Firewalls class
    f = Firewalls()
    # Run the reinit module to re-init the firewall
    f.reinit(id)
    # Flask Message touting the sucess of the reinitialization
    flash('Re-Initialization Started', 'success')
    # Redirect to the default firewall page
    return redirect(url_for('web.firewalls'))


@mod_web.route('/firewall/initall', methods=['GET'])
@login_required
def firewall_init_all():
    # Init the Firewalls class
    f = Firewalls()
    # Reinit all function 
    f.initall()
    # Flash message
    flash('Bulk Initialization Started', 'success')
    # Redirect to the default firewall page
    return redirect(url_for('web.firewalls'))
