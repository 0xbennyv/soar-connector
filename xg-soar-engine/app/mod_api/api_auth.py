# Import the needed Flask Modules
from flask import request, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

# Import module db models
from app.models import Tokens

# Initialize HTTPTokenAuth
token_auth = HTTPTokenAuth()

# Do the token check
@token_auth.verify_token
def verify_token(token):
    user = Tokens.check_token(token) if token else None
    return user is not None


# Bail out error
@token_auth.error_handler
def token_auth_error():
    return jsonify(error="Bad Token"), 401
