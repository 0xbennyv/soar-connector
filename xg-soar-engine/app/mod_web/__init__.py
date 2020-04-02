# Import flask dependencies
from flask import Blueprint, render_template

# Import need Flask Login Dependancies 
from flask_login import login_required

# Define the blueprint: 'web', set its url prefix: app.url/web
mod_web = Blueprint('web', __name__, url_prefix='/web')

# Define rest of the routes
import app.mod_web.web_tokens
import app.mod_web.web_ip
import app.mod_web.web_fqdn
import app.mod_web.web_firewalls
import app.mod_web.web_dashboard
