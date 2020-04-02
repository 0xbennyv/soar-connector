# Import the database object from the main app module
from app import db, rq_ondemand
# Import module db models
from app.models import BlackListIp, Firewalls, Tasks
# Import requests
import requests
# Import Time and Data for Time Delta
from datetime import timedelta
# Import Get Current Job so things can be marked as completed as job runs
from rq import get_current_job

class IPBlackListDelete():

    def ip_blacklist_del(self):
        # Get RQ Worker Job ID
        job = get_current_job()
        # Update status to display started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        if self.fw:
            for fw in self.fw:
                # Query the database for all ip addresses
                q = BlackListIp.query.filter_by(deletion=1).all()
                # Build xml of objects to be deleted
                ips = ""
                for ip in q:
                    ips += f"""
                            <Name>SOAR_{ip.ip}</Name>
                            <IPFamily>IPv4</IPFamily>
                            <HostType>IP</HostType>
                            <IPAddress>{ip.ip}</IPAddress>
                        """
                
                xml = f"""
                    <Request>
                        <Login>
                            <Username>{fw.username}</Username>
                            <Password passwordform="plain">{fw.password}</Password>
                        </Login>
                        <set operation="update">
                            <IPHost>
                            {ips}
                                <HostGroupList>
                                    <Remove>
                                        <HostGroup>SOAR_IP_BlackList</HostGroup>
                                    </Remove>
                                </HostGroupList>
                            </IPHost>
                        </set>
                        <Remove>
                        <IPHost>
                        {ips}
                        </IPHost>
                        </Remove>
                    </Request>"""
                r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)
        # Make the Deletion
        q = BlackListIp.query.filter_by(deletion=1).delete()
        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        # Commit the Session
        db.session.commit()

    def ondemand(self):
        rq_ondemand.enqueue_call(func=self.ip_blacklist_del)

    def __init__(self):
        self.fw = Firewalls().query.all()
