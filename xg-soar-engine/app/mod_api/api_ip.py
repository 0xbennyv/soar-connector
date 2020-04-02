# Import the database object from the main app module
from app import db

# Import the needed Flask Modules
from flask import jsonify

# Import from Standard Libraries

# Import what's needed for Authentication
from app.mod_api.api_auth import token_auth

# Import Validators for input.
from wtforms.validators import IPAddress

# Import module db models
from app.models import BlackListIp, BlackListIpSchema

# Import blueprint mod_api
from app.mod_api import mod_api

# Import the schema's for serializing mutliple and sigular as JSON with Flask-Marshmellow
blacklistip_schema = BlackListIpSchema()
blacklistips_schema = BlackListIpSchema(many=True)

# BlackListing IP's is done here
@mod_api.route('/blacklistip/add/<ip>', methods=['GET'])
@token_auth.login_required
def blacklistip_add(ip):

    # Run a validator to make sure the input is an IP Address. 
    if IPAddress.check_ipv4(ip):
        # Query the database for ip address
        q = BlackListIp.query.filter_by(ip=ip).first()

        # If it's already in database
        if q:
            r = {'error': f'{ip} already blacklisted'}
            return jsonify(r), 404
            
        # else do the good thing
        else:
            q = BlackListIp()
            q.add(ip=ip)
            r = {'success': f'{ip} has been Black Listed'}
            return jsonify(r), 200

    # If the input isn't valid spit an error
    else:
        r = {'error': 'Bad IP address provided'}
        return jsonify(r), 400


# BlackListing IP's is done here
@mod_api.route('/blacklistip/delete/<ip>', methods=['GET'])
@token_auth.login_required
def blacklistip_del(ip):

    # Run a validator to make sure the input is an IP Address. 
    if IPAddress.check_ipv4(ip):
            # Query the database for ip address
            q = BlackListIp.query.filter_by(ip=ip).first()
            # If it's not in database spit error
            if q is None:
                r = {'error': f'{ip} not found'}
                return jsonify(r), 404
            # Else tell us the good news

            else:
                id = q.id
                # Query the database and delete
                q = BlackListIp()
                q.delete(id=id)

                r = {'success': f'{ip} Marked for deletion.'}
                return jsonify(r), 200

    # If the IP ins't valid spit an error
    else:
        r = {'error': 'Bad IP Address Provided'}
        return jsonify(r), 400


# BlackList IP Address - Dump All in DB
@mod_api.route('/blacklistip/list/all', methods=['GET'])
@token_auth.login_required
def blacklistip_list_all():

    # Query all IP's in database
    q = BlackListIp.query.all()
    r = blacklistips_schema.dump(q)

    # Return all IP's in database
    return jsonify(r), 201


# List Blacklist IP for confirmation
@mod_api.route('/blacklistip/list/<ip>', methods=['GET'])
@token_auth.login_required
def blacklistip_list(ip):

    # Check IP Address Validity
    if IPAddress.check_ipv4(ip) is False:
        return jsonify(error="IP Address not a valid format"), 400  

    # Query the database for ip address
    q = BlackListIp.query.filter_by(ip=ip).first()

    # If it's not in database spit error
    if q is None:
        r = {'error': f'{ip} not found'}
        return jsonify(r), 404

    # Else tell us the good news
    else:
        r = {'success': f'{ip} is Black Listed'}
        return jsonify(r), 201
