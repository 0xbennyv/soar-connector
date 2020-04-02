# Import Flask
from flask import Flask
# Import Bootstrap for Styling
from flask_bootstrap import Bootstrap
# Import FlaskSQLAlchemy for ORM and Flask Migreate for DB Upgrades
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Import Marshmellow for dumping DB Schema for JSON
from flask_marshmallow import Marshmallow
# Import Login manager to manage the user
from flask_login import LoginManager
# Redis and RQ for Tash Queuing
from redis import Redis
from rq.registry import ScheduledJobRegistry
import rq

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate()
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

bootstrap = Bootstrap(app)


# Setup REDIS and the 5 different queues.
redis = Redis.from_url(app.config['REDIS_URL'])

# On Demand used for any tasks that manually are invoked.
rq_ondemand = rq.Queue(app.config['RQ_QUEUES'][0], connection=redis)
rq_ondemand_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][0], connection=redis)

# Scheduled Tasks Queues, have the queues and workers seperate
rq_fw = rq.Queue(app.config['RQ_QUEUES'][1], connection=redis)
rq_fw_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][1], connection=redis)

rq_fw_del = rq.Queue(app.config['RQ_QUEUES'][2], connection=redis)
rq_fw_del_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][2], connection=redis)

rq_ip = rq.Queue(app.config['RQ_QUEUES'][3], connection=redis)
rq_ip_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][3], connection=redis)

rq_ip_del = rq.Queue(app.config['RQ_QUEUES'][4], connection=redis)
rq_ip_del_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][4], connection=redis)

rq_fqdn = rq.Queue(app.config['RQ_QUEUES'][5], connection=redis)
rq_fqdn_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][5], connection=redis)

rq_fqdn_del = rq.Queue(app.config['RQ_QUEUES'][6], connection=redis)
rq_fqdn_del_reg = ScheduledJobRegistry(app.config['RQ_QUEUES'][6], connection=redis)



# Import different module blueprints
from app.mod_default.routes import mod_default as default_module
app.register_blueprint(default_module)

from app.mod_auth.routes import mod_auth as auth_module
app.register_blueprint(auth_module)

from app.mod_web import mod_web as web_module
app.register_blueprint(web_module)

from app.mod_api import mod_api as api_module
app.register_blueprint(api_module)

from app.mod_tasks import mod_tasks as tasks_module
app.register_blueprint(tasks_module)

from app.mod_docs import mod_docs as docs_module
app.register_blueprint(docs_module)

# Import DB Models
from app.models import Firewalls, BlackListIp, BlackListFqdn, Tasks, User


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Create DB after building the rest of the APP
db.create_all()
