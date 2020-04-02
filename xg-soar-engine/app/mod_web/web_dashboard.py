from app import db
# Import flask dependencies
from flask import render_template, flash, session, redirect, url_for

# Import Flask Login Dependencies
from flask_login import login_required, current_user

# Import blueprint mod_tokens
from app.mod_web import mod_web

# Import module models
from app.models import Firewalls, Tasks, BlackListFqdn, BlackListIp

@mod_web.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Query to count not initialised devices
    notinit = Firewalls.query.filter_by(initialized=0).count()
    # Query to count devices healthy/online
    online = Firewalls.query.filter_by(health=1).count()
    # Query to count the devices that are in unhealthy states
    health = db.session.execute('SELECT count(id) FROM Firewalls WHERE health = 2 OR health = 0').scalar()
    # List of the most recent tasks
    tasks = Tasks.query.order_by(Tasks.date.desc()).limit(25).all()
    # Query to count all IP's
    total_ip = BlackListIp.query.count()
    # Query to count all fqdn's
    total_fqdn = BlackListFqdn.query.count()
    # Render the template and push the queries
    return render_template('mod_web/index.html', title='XG SOAR Connector', health=health, online=online, \
                            notinit=notinit, tasks=tasks, fqdns=total_fqdn, ips=total_ip)

