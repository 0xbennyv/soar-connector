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


class FirewallInitialize():

    def base_objects_add(self):
        # Get RQ Job
        job = get_current_job()
        # Update the database to say the task is started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        db.session.commit()
        if self.fw:
            for fw in self.fw:
                xml = f"""
                        <Request>
                        <Login>
                            <Username>{fw.username}</Username>
                            <Password passwordform="plain">{fw.password}</Password>
                        </Login>
                        <SET operation="add">
                            <IPHostGroup>
                                <Name>SOAR_IP_BlackList</Name>
                                <Description/>
                                <HostList>
                                </HostList>
                                <IPFamily>IPv4</IPFamily>
                            </IPHostGroup>
                        </SET>
                        <Set operation="add">
                            <FQDNHostGroup>
                                <Name>SOAR_FQDN_BlackList</Name>
                                <Description>Distributed from the XG SOAR Connector</Description>
                                <FQDNHostList>
                                </FQDNHostList>
                            </FQDNHostGroup>
                        </Set>
                        <Set operation="add">
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
                        </Set>
                        </Request>"""
            # Request for to XML API
            r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

            # Mark task as completed
            Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
            
            # Update the Device Health and Init status
            q = Firewalls.query.filter_by(id=fw.id).first()
            q.initialized = 1
            q.health = 1
            db.session.commit()

    def host_objects_add(self):
        # Get RQ Worker Job ID
        job = get_current_job()
        # Update task status so it displays as started
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 2})
        db.session.commit()
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
                        <Set operation="add">
                            {fqdns}
                        </Set>
                    </Request>"""
                    # Request for to XML API
                    r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

                # Query the database for all ip addresses
                q = BlackListIp.query.all()
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
                        </IPHost>
                        """

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
                    # Request for to XML API
                    r = requests.get(f'https://{fw.ip}:{fw.port}/webconsole/APIController?reqxml={xml}', verify=False, timeout=60)

        # Mark task as completed
        Tasks.query.filter_by(id=job.id).update({Tasks.complete: 1})
        db.session.commit()

    def __init__(self, fw):
        self.fw = fw

