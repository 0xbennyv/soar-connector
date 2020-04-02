# Import the needed Flask Modules
from flask import request, jsonify

# Import from Standard Libraries
import json

# Import what's needed for Authentication
from app.mod_api.api_auth import token_auth

# Import the tasks that's going to get executed from API
from app.mod_tasks.firewall_staging import FirewallInitialize
from app.mod_tasks.ip_add import IPBlackListDistribute
from app.mod_tasks.fqdn_add import FqdnBlackListDistribute

# Import module db models
from app.models import Firewalls

# Import blueprint mod_api
from app.mod_api import mod_api

@mod_api.route('/run/firewalls/init', methods=['GET'])
@token_auth.login_required
def initialize_firewall():

    fw = Firewalls().query.filter_by(initialized=0).all()
    if fw:
        FirewallInitialize().ondemand(fw)
        return jsonify(success=f"Initialization Started"), 201
    else:
        return jsonify(error="No firewalls to initialize")
    

@mod_api.route('/run/distribute/ips', methods=['GET'])
@token_auth.login_required
def distribute_ips():

    IPBlackListDistribute().ondemand()
    # Return the default message in JSON Format.
    return jsonify(success='Distribution for IP BlackList has begun')


@mod_api.route('/run/distribute/fqdns', methods=['GET'])
@token_auth.login_required
def distribute_fqdns():

    FqdnBlackListDistribute().ondemand()
    # Return the default message in JSON Format.
    return jsonify(success='Distribution for FQDN BlackList has begun')
