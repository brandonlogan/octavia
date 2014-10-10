#    Copyright 2014 Rackspace
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Defines interface for DB access that Resource or Octavia Controllers may
reference
"""

from octavia.common import constants
from octavia.common import exceptions
from octavia.db import models
from octavia.openstack.common import uuidutils


class BaseRepository(object):

    model_class = None

    def create(self, session, **model_kwargs):
        with session.begin(subtransactions=True):
            model = self.model_class(**model_kwargs)
            session.add(model)
        return model.to_data_model()

    def delete(self, session, **filters):
        model = session.query(self.model_class).filter_by(**filters).first()
        with session.begin(subtransactions=True):
            session.delete(model)
            session.flush()

    def delete_batch(self, session, ids=None):
        [self.delete(session, id) for id in ids]

    def update(self, session, id, **model_kwargs):
        with session.begin(subtransactions=True):
            session.query(self.model_class).filter_by(
                id=id).update(model_kwargs)

    def get(self, session, **filters):
        model = session.query(self.model_class).filter_by(**filters).first()
        if not model:
            return
        return model.to_data_model()

    def get_all(self, session, **filters):
        model_list = session.query(self.model_class).filter_by(**filters).all()
        data_model_list = [model.to_data_model() for model in model_list]
        return data_model_list

    def exists(self, session, id):
        return bool(session.query(self.model_class).filter_by(id=id).first())


class Repositories(object):

    def __init__(self):
        self.load_balancer = LoadBalancerRepository()
        self.vip = VipRepository()
        self.health_monitor = HealthMonitorRepository()
        self.session_persistence = SessionPersistenceRepository()
        self.pool = PoolRepository()
        self.member = MemberRepository()
        self.listener = ListenerRepository()
        self.listener_stats = ListenerStatisticsRepository()
        self.amphora = AmphoraRepository()
        self.sni = SNIRepository()

    def create_load_balancer_and_vip(self, session, load_balancer_dict,
                                     vip_dict):
        with session.begin():
            load_balancer_dict['id'] = uuidutils.generate_uuid()
            lb = models.LoadBalancer(**load_balancer_dict)
            session.add(lb)
            vip_dict['load_balancer_id'] = load_balancer_dict['id']
            vip = models.Vip(**vip_dict)
            session.add(vip)
        return self.load_balancer.get(session, id=lb.id)

    def create_pool_on_listener(self, session, listener_id,
                                pool_dict, sp_dict=None):
        with session.begin(subtransactions=True):
            pool_dict['id'] = uuidutils.generate_uuid()
            db_pool = self.pool.create(session, **pool_dict)
            if sp_dict:
                sp_dict['pool_id'] = pool_dict['id']
                self.session_persistence.create(session, **sp_dict)
            self.listener.update(session, listener_id,
                                 default_pool_id=pool_dict['id'])
        return self.pool.get(session, id=db_pool.id)

    def update_pool_on_listener(self, session, pool_id, pool_dict, sp_dict):
        with session.begin(subtransactions=True):
            self.pool.update(session, pool_id, **pool_dict)
            if sp_dict:
                if self.session_persistence.exists(session, pool_id):
                    self.session_persistence.update(session, pool_id,
                                                    **sp_dict)
                else:
                    sp_dict['pool_id'] = pool_id
                    self.session_persistence.create(session, **sp_dict)
        db_pool = self.pool.get(session, id=pool_id)
        if db_pool.session_persistence is not None and not sp_dict:
            self.session_persistence.delete(session, pool_id=pool_id)
            db_pool = self.pool.get(session, id=pool_id)
        return db_pool


class LoadBalancerRepository(BaseRepository):

    model_class = models.LoadBalancer

    def test_and_set_provisioning_status(self, session, id, status):
        with session.begin(subtransactions=True):
            lb = session.query(self.model_class).with_for_update().filter_by(
                id=id).one()
            if lb.provisioning_status not in constants.MUTABLE_STATUSES:
                raise exceptions.ImmutableStatus
            lb.provisioning_status = status
            session.add(lb)


class VipRepository(BaseRepository):

    model_class = models.Vip

    def update(self, session, load_balancer_id, **model_kwargs):
        with session.begin(subtransactions=True):
            session.query(self.model_class).filter_by(
                load_balancer_id=load_balancer_id).update(model_kwargs)


class HealthMonitorRepository(BaseRepository):

    model_class = models.HealthMonitor

    def update(self, session, pool_id, **model_kwargs):
        with session.begin(subtransactions=True):
            session.query(self.model_class).filter_by(
                pool_id=pool_id).update(model_kwargs)


class SessionPersistenceRepository(BaseRepository):

    model_class = models.SessionPersistence

    def update(self, session, pool_id, **model_kwargs):
        with session.begin(subtransactions=True):
            session.query(self.model_class).filter_by(
                pool_id=pool_id).update(model_kwargs)

    def exists(self, session, pool_id):
        return bool(session.query(self.model_class).filter_by(
            pool_id=pool_id).first())


class PoolRepository(BaseRepository):

    model_class = models.Pool


class MemberRepository(BaseRepository):

    model_class = models.Member

    def delete_members(self, session, member_ids):
        self.delete_batch(session, member_ids)


class ListenerRepository(BaseRepository):

    model_class = models.Listener

    def has_pool(self, session, id):
        listener = self.get(session, id=id)
        if listener.default_pool:
            return True
        return False


class ListenerStatisticsRepository(BaseRepository):

    model_class = models.ListenerStatistics

    def update(self, session, listener_id, **model_kwargs):
        with session.begin(subtransactions=True):
            session.query(self.model_class).filter_by(
                listener_id=listener_id).update(model_kwargs)


class AmphoraRepository(BaseRepository):

    model_class = models.Amphora

    def associate(self, session, load_balancer_id, amphora_id):
        with session.begin(subtransactions=True):
            load_balancer = session.query(models.LoadBalancer).filter_by(
                id=load_balancer_id).first()
            amphora = session.query(self.model_class).filter_by(
                id=amphora_id).first()
            load_balancer.amphorae.append(amphora)


class SNIRepository(BaseRepository):

    model_class = models.SNI

    def update(self, session, listener_id=None, tls_container_id=None,
               **model_kwargs):
        if not listener_id and tls_container_id:
            raise exceptions.MissingArguments
        with session.begin(subtransactions=True):
            if listener_id:
                session.query(self.model_class).filter_by(
                    listener_id=listener_id).update(model_kwargs)
            elif tls_container_id:
                session.query(self.model_class).filter_by(
                    tls_container_id=tls_container_id).update(model_kwargs)
