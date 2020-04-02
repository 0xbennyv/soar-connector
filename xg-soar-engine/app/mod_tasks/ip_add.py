# Import the database object from the main app module
from app import db, rq_ondemand
# Import module db models
from app.models import BlackListIp, Firewalls, Tasks
# Import requests
import requests
# Import Time and Data for Time Delta
from datetime import timedelta, datetime
# Import Get Current Job so things can be marked as completed as job runs
from rq import get_current_job

class IPBlackListDistribute():
    
    def distribute(self):
        # Get RQ Worker Job ID
        job = get_current_job()
        # Update Tasks to status Started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        # Get All Firewalls to distribute too.
        q = Firewalls.query.all()
        for fw in q:
            # Query the database for all ip addresses
            q = BlackListIp.query.filter_by(distributed=0).all()
            # get the IP Address and put it in a list
            for ip in q:
                ips = f"""
                        <IPHost>
                            <Name>SOAR_{ip.ip}</Name>
                            <IPFamily>IPv4</IPFamily>
                            <HostType>IP</HostType>
                            <IPAddress>{ip.ip}</IPAddress>
                            <HostGroupList>
                                <HostGroup>SOAR_IP_BlackList</HostGroup>
                            </HostGroupList>
                        </IPHost>"""
                
                xml = f"""
                    <Request>
                    <Login>
                        <Username>{fw.username}</Username>
                        <Password passwordform="plain">{fw.password}</Password>
                    </Login>
                        <Set operation="add">
                            {ips}
                        </Set>
                    </Request>"""
                r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        # Mark IP Addresses as distributed
        BlackListIp.query.update({BlackListIp.distributed: 1})
        # Commit the data so it's not left in the memory of a compter somewhere
        db.session.commit()
                
    def ondemand(self):
        rq_ondemand.enqueue_call(func=self.distribute)

