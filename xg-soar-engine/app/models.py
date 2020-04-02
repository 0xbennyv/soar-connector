from flask_login import UserMixin
from app import db, ma 
from app import rq_ondemand, rq_ip, rq_ip_reg, rq_ip_del, rq_ip_del_reg
from app import rq_fqdn, rq_fqdn_reg, rq_fqdn_del, rq_fqdn_del_reg
from app import rq_fw, rq_fw_reg, rq_fw_del, rq_fw_del_reg
from datetime import timedelta, timezone, datetime
import os
import base64
# Imports for mod_tasks are at the bottom, due to app initialization (app/__init__.py) sequence
# *** It's not a bug it's a feature ***


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(1024))


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    token = db.Column(db.String(32), index=True)
    name = db.Column(db.String(120), index=True)
    description = db.Column(db.String(120), index=True)
    expiration = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)

    def add(self, name, description, user_id, expires):
        now = datetime.utcnow()
        token = base64.b64encode(os.urandom(24)).decode('utf-8')
        expiration = now + timedelta(days=int(expires))
        q = Tokens(token=token, name=name, description=description, expiration=expiration, user_id=user_id)
        db.session.add(q)
        db.session.commit()

    def expire(self, id):
        q = Tokens.query.filter_by(id=id).first()
        q.expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()

    def delete(self, id):
        q = Tokens.query.filter_by(id=id).delete()
        db.session.commit()

    @staticmethod
    def check_token(token):
        t = Tokens.query.filter_by(token=token).first()
        if t is None or t.expiration < datetime.utcnow():
            return None
        return t


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'email', 'firstname', 'lastname', 'token', 'token_expiration')
        ordered = True


class Firewalls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fwname = db.Column(db.String(120), index=True)
    username = db.Column(db.String(120), index=True)
    password = db.Column(db.String(120), index=True)
    ip = db.Column(db.String(120), index=True)
    port = db.Column(db.Integer, index=True)
    initialized = db.Column(db.Integer, index=True)
    health = db.Column(db.Integer, index=True)
    deletion = db.Column(db.Integer, index=True)

    def add(self, fwname, username, password, ip, port, init):
        q = Firewalls(fwname=fwname, username=username, password=password,\
                      ip=ip, port=port, initialized=init, health=2, deletion=0)
        db.session.add(q)
        db.session.commit()
        # This whole Block needs some work, weird behavior with session and the tasks sharing the all() queries
        if init == 1:
            
            fw = Firewalls.query.filter_by(ip=ip).all()
            job = rq_ondemand.enqueue_in(timedelta(seconds=10), func=FirewallInitialize(fw).base_objects_add)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name=f'{fwname} base config initialization', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()

            fw = Firewalls.query.filter_by(ip=ip).all()
            job = rq_ondemand.enqueue_in(timedelta(seconds=30),FirewallInitialize(fw).host_objects_add)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name=f'{fwname} host objects initalization', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()

        else:
            # This stops multiple queues by getting the job register and making sure there's not already 2 in there.
            if len(rq_fw_reg.get_job_ids()) < 2:
                fw = Firewalls().query.filter_by(initialized=0).all()
                job = rq_fw.enqueue_in(timedelta(seconds=300), func=FirewallInitialize(fw).base_objects_add)
                t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='Firewalls base config initialization', complete=0, user_id=0)
                db.session.add(t)
                db.session.commit()

                fw = Firewalls().query.filter_by(initialized=0).all()
                job = rq_fw.enqueue_in(timedelta(seconds=330), func=FirewallInitialize(fw).host_objects_add)
                t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='Firewalls host objects initalization', complete=0, user_id=0)
                db.session.add(t)
                db.session.commit()

    def update(self, id, fwname, username, ip, port):
        q = Firewalls.query.filter_by(id=id).first()
        q.fwname=fwname
        q.username=username
        q.ip=ip
        q.port=port
        db.session.commit()
        
        q = Firewalls.query.filter_by(id=id).all()
        FirewallChecks(q).auth_check()

    def delete(self, id):
        Firewalls.query.filter_by(id=id).delete()
        db.session.commit()
    
    def decommision(self, id):
        q = Firewalls.query.filter_by(id=id).first()
        q.deletion = 1
        db.session.commit()

        # This stops multiple queues by getting the job register and making sure there's not already 2 in there.
        if len(rq_fw_del_reg.get_job_ids()) < 2:
            job = rq_fw_del.enqueue_in(timedelta(seconds=600), func=FirewallDecommission().base_objects_del)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='Firewalls base config decommision', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()

            job = rq_fw_del.enqueue_in(timedelta(seconds=630), func=FirewallDecommission().host_objects_del)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='Firewalls host object decommision', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()

    def reinit(self, fw):  

        fw = Firewalls.query.filter_by(id=fw).all()
        job = rq_ondemand.enqueue_in(timedelta(seconds=10), func=FirewallInitialize(fw).base_objects_add)
        t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name=f'Firewall Base config re-initialization', complete=0, user_id=0)
        db.session.add(t)

        job = rq_ondemand.enqueue_in(timedelta(seconds=30), func=FirewallInitialize(fw).host_objects_add)
        t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name=f'Firewall Host objects re-initalization', complete=0, user_id=0)
        db.session.add(t)
        db.session.commit()
    
    def initall(self):  

        fw = Firewalls.query.all()
        job = rq_ondemand.enqueue_in(timedelta(seconds=10), func=FirewallInitialize(fw).base_objects_add)
        t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name=f'Bulk Initialization Started', complete=0, user_id=0)
        db.session.add(t)

        job = rq_ondemand.enqueue_in(timedelta(seconds=30), func=FirewallInitialize(fw).host_objects_add)
        t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name=f'Bulk Initialization Started', complete=0, user_id=0)
        db.session.add(t)
        db.session.commit()


class FirewallSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'fwname', 'username', 'password', 'ip', 'port', 'initialized', 'health', 'deletion')
        ordered = True


class BlackListIp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(120), index=True)
    distributed = db.Column(db.Integer, index=True)
    deletion = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer)

    def add(self, ip):
        q = BlackListIp(ip=ip, user_id=0, distributed=0, deletion=0)
        db.session.add(q)
        db.session.commit()
        if len(rq_ip_reg.get_job_ids()) < 1:
            job = rq_ip.enqueue_in(timedelta(seconds=300), func=IPBlackListDistribute().distribute)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='IP Distribution', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()

    def delete(self, id):
        q = BlackListIp.query.filter_by(id=id).first()
        q.deletion = 1
        db.session.add(q)
        db.session.commit()
        if len(rq_ip_del_reg.get_job_ids()) < 1:
            job = rq_ip_del.enqueue_in(timedelta(seconds=300), func=IPBlackListDelete().ip_blacklist_del)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='IP Deletion', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()



class BlackListIpSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'ip', 'distributed', 'deletion')
        ordered = True


class BlackListFqdn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fqdn = db.Column(db.String(120), index=True)
    distributed = db.Column(db.Integer, index=True)
    deletion = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer)

    def add(self, fqdn):
        q = BlackListFqdn(fqdn=fqdn, user_id=0, distributed=0, deletion=0)
        db.session.add(q)
        db.session.commit()
        if len(rq_fqdn_reg.get_job_ids()) < 1:
            job = rq_fqdn.enqueue_in(timedelta(seconds=300), func=FqdnBlackListDistribute().distribute)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='FQDN Distribution', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()
    
    def delete(self, id):
        q = BlackListFqdn.query.filter_by(id=id).first()
        q.deletion = 1
        db.session.add(q)
        db.session.commit()
        if len(rq_fqdn_del_reg.get_job_ids()) < 1:
            job = rq_fqdn_del.enqueue_in(timedelta(seconds=300), func=FqdnBlackListDelete().fqdn_blacklist_group_del)
            t = Tasks(id=f'{job.get_id()}', date=f'{datetime.now()}', name='FQDN Deletion', complete=0, user_id=0)
            db.session.add(t)
            db.session.commit()


class BlackListFqdnSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'fqdn', 'distributed', 'deletion')
        ordered = True


class Tasks(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    date = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128), index=True)
    complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer)


# Due to the App Builder imports need to be down here.
from app.mod_tasks.ip_add import IPBlackListDistribute
from app.mod_tasks.ip_del import IPBlackListDelete
from app.mod_tasks.fqdn_add import FqdnBlackListDistribute
from app.mod_tasks.fqdn_del import FqdnBlackListDelete
from app.mod_tasks.firewall_staging import FirewallInitialize
from app.mod_tasks.firewall_decommission import FirewallDecommission
from app.mod_tasks.firewall_checks import FirewallChecks

