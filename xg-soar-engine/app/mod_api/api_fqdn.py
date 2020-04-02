# Import the database object from the main app module
from app import db

# Import the needed Flask Modules
from flask import jsonify

# Import from Standard Libraries
import re

# Import what's needed for Authentication
from app.mod_api.api_auth import token_auth

# Import module db models
from app.models import BlackListFqdn, BlackListFqdnSchema

# Import blueprint mod_api
from app.mod_api import mod_api

# Import the schema's for serializing mutliple and sigular as JSON with Flask-Marshmellow
blacklistfqdn_schema = BlackListFqdnSchema()
blacklistfqdns_schema = BlackListFqdnSchema(many=True)

# BlackListing FQDN's is done here
@mod_api.route('/blacklistfqdn/add/<fqdn>', methods=['GET'])
@token_auth.login_required
def blacklistfqdn_add(fqdn):

    # Run a validator to make sure the input is an IP Address. 
    if re.match(r'^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$', fqdn):
        # Query the database for ip address
        q = BlackListFqdn.query.filter_by(fqdn=fqdn).first()
        # If it's already in database
        if q:
            r = {'error': f'{fqdn} already blacklisted'}
            return jsonify(r), 404
        # else do the good thing
        else:
            q = BlackListFqdn()
            q.add(fqdn=fqdn)
            r = {'success': f'{fqdn} has been Black Listed'}
            return jsonify(r), 200
    # If the input isn't valid spit an error
    else:
        r = {'error': 'Bad FQDN provided'}
        return jsonify(r), 400


# BlackListing IP's is done here
@mod_api.route('/blacklistfqdn/delete/<fqdn>', methods=['GET'])
@token_auth.login_required
def blacklistfqdn_del(fqdn):

    # Run a validator to make sure the input is a domain or fqdn
    if re.match(r'^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$', fqdn):
            # Query the database for ip address
            q = BlackListFqdn.query.filter_by(fqdn=fqdn).first()
            
            # If it's not in database spit error
            if q is None:
                r = {'error': f'{fqdn} not found'}
                return jsonify(r), 404

            # Else tell us the good news
            else:
                id = q.id
                # Query the database and delete
                q = BlackListFqdn()
                q.delete(id=id)
                r = {'success': f'{fqdn} Deleted'}
                return jsonify(r), 200

    # If the IP ins't valid spit an error
    else:
        r = {'error': 'Bad FQDN Provided'}
        return jsonify(r), 400


# BlackList IP Address - Dump All in DB
@mod_api.route('/blacklistfqdn/list/all', methods=['GET'])
@token_auth.login_required
def blacklistfqdn_list_all():

    # Query all IP's in database
    q = BlackListFqdn.query.all()
    r = blacklistfqdns_schema.dump(q)

    # Return all IP's in database
    return jsonify(r), 201


# List Blacklist IP for confirmation
@mod_api.route('/blacklistfqdn/list/<fqdn>', methods=['GET'])
@token_auth.login_required
def blacklistfqdn_list(fqdn):

    # Run a validator to make sure the input is an IP Address. 
    if re.match(r'^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$', fqdn):
        # Query the database for ip address
        q = BlackListFqdn.query.filter_by(fqdn=fqdn).first()

        # If it's not in database spit error
        if q is None:
            r = {'error': f'{fqdn} not found'}
            return jsonify(r), 404
            
        # Else tell us the good news
        else:
            r = {'success': f'{fqdn} is Black Listed'}
            return jsonify(r), 201

    # If the IP ins't valid spit an error
    else:
        r = {'error': 'Bad FQDN Provided'}
        return jsonify(r), 400