# Import the database object from the main app module
from app import db, rq_ondemand
# Import module db models
from app.models import BlackListFqdn, Firewalls, Tasks
# Import requests
import requests
# Import Time and Data for Time Delta
from datetime import timedelta
# Import Get Current Job so things can be marked as completed as job runs
from rq import get_current_job

class FqdnBlackListDelete():

    def fqdn_blacklist_group_del(self):
        # Get RQ Worker Job ID
        job = get_current_job()
        # Update the Task status to display as started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        if self.fw:
            for fw in self.fw:
                # Query the database for all ip addresses
                q = BlackListFqdn.query.filter_by(deletion=1).all()
                # get the IP Address and put it in a list
                fqdns = ""
                for f in q:
                    fqdns += f"""
                                <Name>SOAR_{f.fqdn}</Name>
                                <FQDN>SOAR_{f.fqdn}</FQDN>
                            """

                xml = f"""
                <Request>
                    <Login>
                        <Username>{fw.username}</Username>
                        <Password passwordform="plain">{fw.password}</Password>
                    </Login>
                    <set operation="update">
                    <FQDNHost>
                    {fqdns}
                        <FQDNHostGroupList>
                            <Remove>
                                <FQDNHostGroup>SOAR_FQDN_BlackList</FQDNHostGroup>
                            </Remove>
                        </FQDNHostGroupList>
                    </FQDNHost>
                    </set>
                    <Remove>
                    <FQDNHost>
                        {fqdns}
                    </FQDNHost>
                    </Remove>
                    </Request>"""
                # Request for to XML API
                r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

        # Delete All IP Addresses marked for Deletion
        q = BlackListFqdn.query.filter_by(deletion=1).delete()
        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        # Mark FQDN as distributed
        BlackListFqdn.query.update({BlackListFqdn.distributed: 1}) 
        #Commit the session
        db.session.commit()

    def ondemand(self):
        rq_ondemand.enqueue_call(func=self.fqdn_blacklist_group_del)
    
    def __init__(self):
        self.fw = Firewalls().query.all()
