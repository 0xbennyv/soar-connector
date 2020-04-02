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


class FqdnBlackListDistribute():

    def distribute(self):
        # Get RQ Worker Job ID
        job = get_current_job()
        # Update tasks status to display as started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        q = Firewalls.query.all()
        for fw in q:
            # Query the database for all ip addresses
            q = BlackListFqdn.query.filter_by(distributed=0).all()
            # get the IP Address and put it in a list
            for f in q:
                fqdns = f"""
                    <FQDNHost>
                        <Name>SOAR_{f.fqdn}</Name>
                        <FQDN>{f.fqdn}</FQDN>
                        <FQDNHostGroupList>
                            <FQDNHostGroup>SOAR_FQDN_BlackList</FQDNHostGroup>
                        </FQDNHostGroupList>
                    </FQDNHost>
                    """

                xml = f"""
                <Request>
                    <Login>
                        <Username>{fw.username}</Username>
                        <Password passwordform="plain">{fw.password}</Password>
                    </Login>
                    <Set operation="add">
                        {fqdns}
                    </Set>
                </Request>"""
                # Request for to XML API
                r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        # Mark FQDN as distributed
        BlackListFqdn.query.update({BlackListFqdn.distributed: 1}) 
        #Commit the session
        db.session.commit()


    def ondemand(self):
        rq_ondemand.enqueue_call(func=self.distribute)
