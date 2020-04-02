# Import the needed Flask Modules
from flask import request, jsonify, Blueprint

# Import from Standard Libraries
import json

# Import module db models
from app.models import Firewalls, FirewallSchema

# Import Tasks that may arrise from these shenanigans
from app.mod_tasks.firewall_staging import FirewallInitialize

# Import what's needed for Authentication
from app.mod_api.api_auth import token_auth

# Import Validators for input.
from wtforms.validators import IPAddress

# Import blueprint mod_api
from app.mod_api import mod_api

# Import the schema's for serializing mutliple and sigular as JSON with Flask-Marshmellow
firewall_schema = FirewallSchema()
firewalls_schema = FirewallSchema(many=True)

# Add Firewall via API
@mod_api.route('/firewall/add', methods=['POST'])
@token_auth.login_required
def firewall_add():

    d = request.get_data()
    j = json.loads(d.decode("utf-8"))

    # Check to make sure all the needed infomation is there.
    if 'fwname' not in j or 'username' not in j or 'password' not in j \
        or 'ip' not in j or 'port' not in j or 'init' not in j:
        return jsonify(message='Missing required fields'), 400

    # Check for Duplicate Names
    if Firewalls.query.filter_by(fwname=j['fwname']).first():
        return jsonify(message='Firewall name already in use'), 400

    # Check fo Duplicate IP     
    if Firewalls.query.filter_by(ip=j['ip']).first():
        return jsonify(message='IP Address already in use'), 400

    # Check to see if IP is valid
    if IPAddress.check_ipv4(j['ip']) is False:
        return jsonify(message="IP Address not a valid format"), 400

    # Init the Firewalls Class
    q = Firewalls()
    # Run the add module
    q.add(fwname=j['fwname'], username=j['username'],password=j['password'],\
                    ip=j['ip'],port=j['port'], init=j['init'])

    # Return Success
    r = {'success' : 'Successfully Added Firewall'}
    return jsonify(r), 200


# Delete Firewall
@mod_api.route('/firewall/delete/<id>', methods=['GET'])
@token_auth.login_required
def firewall_del(id):

    # Query for firewall ID to make sure it exists
    q = Firewalls.query.filter_by(id=id).first()

    # If it's not in database spit error
    if q is None:
        r = {'error': 'Firewall not found'}
        return jsonify(r), 404

    # Else tell us the good news
    else:
        # Init the Firewalls Class
        q = Firewalls()
        # Run the Delete Module
        q.delete(id=id)
        r = {'success': 'Firewall Deleted'}
        return jsonify(r), 200


# List all Firewalls
@mod_api.route('/firewall/list/all', methods=['GET'])
@token_auth.login_required
def firewall_all():
    # Query All
    q = Firewalls.query.all()
    # Run schema dump fields set in models.py
    r = firewalls_schema.dump(q)
    # Return JSON
    return jsonify(r), 201


# List firewall by ID - Need to do this better.
@mod_api.route('/firewall/list/<id>', methods=['GET'])
@token_auth.login_required
def firewall_list(id):
    # Run the query
    q = Firewalls.query.filter_by(id=id).first()
    # Check to make sure it exists
    if q is None:
        r = {'error': 'Firewall not found'}
        return jsonify(r), 404

    # Dump the schema if it does
    else:
        r = firewall_schema.dump(q)
        return jsonify(r), 201

