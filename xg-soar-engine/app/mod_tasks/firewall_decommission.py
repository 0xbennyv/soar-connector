# Import the database object from the main app module
from app import db
# Import module db models
from app.models import BlackListIp, Firewalls, BlackListFqdn, Tasks
# Import requests
import requests
# JSONIFY because it's RAD^Sick
from flask import jsonify
# Import Time and Data for Time Delta
from datetime import timedelta
# Import Get Current Job so things can be marked as completed as job runs
from rq import get_current_job

class FirewallDecommission():

    def base_objects_del(self):
        # Get Job ID
        job = get_current_job()
        # Update the status to 2 so it's marked at started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        if self.fw:
            for fw in self.fw:
                xml = f"""
                        <Request>
                        <Login>
                            <Username>{fw.username}</Username>
                            <Password passwordform="plain">{fw.password}</Password>
                        </Login>
                        <Remove>
                            <FirewallRule>
                                <Name>SOAR_Blacklists</Name>
                                <Description/>
                                <IPFamily>IPv4</IPFamily>
                                <Status>Enable</Status>
                                <Position>Top</Position>
                                <PolicyType>Network</PolicyType>
                                <NetworkPolicy>
                                    <Action>Drop</Action>
                                    <LogTraffic>Enable</LogTraffic>
                                    <SkipLocalDestined>Disable</SkipLocalDestined>
                                    <DestinationZones>
                                        <Zone>WAN</Zone>
                                    </DestinationZones>
                                    <Schedule>All The Time</Schedule>
                                    <DestinationNetworks>
                                        <Network>SOAR_IP_BlackList</Network>
                                        <Network>SOAR_FQDN_BlackList</Network>
                                    </DestinationNetworks>
                                </NetworkPolicy>
                            </FirewallRule>
                        </Remove>
                        <Remove>
                            <IPHostGroup>
                                <Name>SOAR_IP_BlackList</Name>
                                <Description/>
                                <HostList>
                                </HostList>
                                <IPFamily>IPv4</IPFamily>
                            </IPHostGroup>
                        </Remove>
                        <Remove>
                            <FQDNHostGroup>
                                <Name>SOAR_FQDN_BlackList</Name>
                                <Description>Distributed from the XG SOAR Connector</Description>
                                <FQDNHostList>
                                </FQDNHostList>
                            </FQDNHostGroup>
                        </Remove>
                        </Request>"""
                # Request for to XML API
                r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        db.session.commit()

    # Have to do a bunch of small requests, there's a max size limit
    def host_objects_del(self):
        # Get Job ID
        job = get_current_job()
        # Update the Tasks to 2 so the status is started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        if self.fw:
            for fw in self.fw:
                # Query the database for all ip addresses
                q = BlackListFqdn.query.all()
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
                            <Remove>
                                {fqdns}
                            </Remove>
                        </Request>"""
                    # Request for to XML API
                    r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

                # Query the database for all ip addresses
                q = BlackListIp.query.all()
                for i in q:
                    ips = f"""
                        <IPHost>
                            <Name>SOAR_{i.ip}</Name>
                            <IPFamily>IPv4</IPFamily>
                            <HostType>IP</HostType>
                            <IPAddress>{i.ip}</IPAddress>
                            <HostGroupList>
                                <HostGroup>SOAR_IP_BlackList</HostGroup>
                            </HostGroupList>
                        </IPHost>
                        """

                    xml = f"""
                    <Request>
                        <Login>
                            <Username>{fw.username}</Username>
                            <Password passwordform="plain">{fw.password}</Password>
                        </Login>
                        <Remove>
                            {ips}
                        </Remove>
                    </Request>"""
                    # Request for to XML API
                    r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)
            
            # Delete the Firewall out of Database
            q = Firewalls.query.filter_by(id=fw.id).delete()
            db.session.commit()
        
        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        db.session.commit()


    def __init__(self):
        self.fw = Firewalls().query.filter_by(deletion=1).all()

