# Import the database object from the main app module
from app import db, rq_ondemand, rq_ondemand_reg
# Import requests
import requests
# Import Time and Data for Time Delta
from datetime import timedelta
# Import Models
from app.models import Firewalls
# Import the XML Parser
import xml.etree.ElementTree as ET

class FirewallChecks():
    # Run an auth check to see if credentials are working
    def auth_check(self):

        for fw in self.fw:
            # XML Request for an auth check
            xml = f"""
                <Request>
                    <Login>
                        <Username>{fw.username}</Username>
                        <Password passwordform="plain">{fw.password}</Password>
                    </Login>
                </Request>"""
            # Try the auth request
            try:
                # Run request
                r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=15)
                # Get the request content
                root = ET.fromstring(r.content)
                # Process the XML Request
                status = root[0][0].text
                # If sucessful then update the health to 1
                if status == 'Authentication Successful':
                    q = Firewalls.query.filter_by(id=fw.id).first()
                    q.health = 1
                    db.session.commit()
                # If it's not successful set it to 0
                else:
                    q = Firewalls.query.filter_by(id=fw.id).first()
                    q.health = 0
                    db.session.commit()
            # if it errors out then set the health to 0
            except:
                q = Firewalls.query.filter_by(id=fw.id).first()
                q.health = 0
                db.session.commit()
                

    def __init__(self, fw):
        self.fw = fw
        rq_ondemand.enqueue_call(func=self.auth_check)
