from flask import Blueprint

# Define the blueprint: 'tasks', set its url prefix: app.url/tasks
mod_tasks = Blueprint('tasks', __name__, url_prefix='/tasks')

from app.mod_tasks.firewall_staging import FirewallInitialize
from app.mod_tasks.ip_add import IPBlackListDistribute
from app.mod_tasks.ip_del import IPBlackListDelete
from app.mod_tasks.fqdn_add import FqdnBlackListDistribute
from app.mod_tasks.fqdn_del import FqdnBlackListDelete
from app.mod_tasks.firewall_checks import FirewallChecks
from app.mod_tasks.firewall_decommission import FirewallDecommission