# Import flask dependencies
from flask import Blueprint, render_template

# Define the blueprint: 'docs', set its url prefix: app.url/docs
mod_docs = Blueprint('docs', __name__, url_prefix='/docs')

# Quick Dirty Stats
@mod_docs.route('/', methods=['GET'])
def index():
    return render_template('mod_docs/index.html')

