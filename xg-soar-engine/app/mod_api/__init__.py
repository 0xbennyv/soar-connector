# Import the needed Flask Modules
from flask import Blueprint, jsonify
from app import db
# Import module db models
from app.models import Firewalls, Tasks, BlackListFqdn, BlackListIp, User

# Set the blueprint
mod_api = Blueprint('api', __name__, url_prefix='/api')

# Import other fonctions on mod_api is set
from app.mod_api import api_firewalls
from app.mod_api import api_ip
from app.mod_api import api_fqdn
from app.mod_api import api_tasks

# Default Response from API Engine
@mod_api.route('/', methods=['GET'])
def index():
    q = User().query.all()
    if q:
        # Return the default message in JSON Format.
        return jsonify(message='SOAR Connector - check out /docs for documentation')
    else:
        return jsonify(message='SOAR Connector, log into web GUI to initialize the instance.')

# Quick Dirty Stats
@mod_api.route('/stats', methods=['GET'])
def stats():
    # Query to count not initialised devices
    notinit = Firewalls.query.filter_by(initialized=0).count()
    # Query to count devices healthy/online
    online = Firewalls.query.filter_by(health=1).count()
    # Query to count the devices that are in unhealthy states
    health = db.session.execute('SELECT count(id) FROM Firewalls WHERE health = 2 OR health = 0').scalar()
    # Query to count all IP's
    total_ip = BlackListIp.query.count()
    # Query to count all fqdn's
    total_fqdn = BlackListFqdn.query.count()
    # Render the template and push the queries
    r = {'total-ips': f'{total_ip}', 'total-fqdns' : f'{total_fqdn}', 'not-initialized' : f'{notinit}', \
        'online' : f'{online}', 'unhealthy' : f'{health}'}
    return jsonify(r), 200


