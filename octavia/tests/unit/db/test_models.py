# Copyright 2014 Octavia
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

from octavia.common import constants
from octavia.db import models
from octavia.tests.unit.db import base


class ModelTestMixin(object):

    FAKE_UUID = '0123456789012345678901234567890123456'

    def _insert(self, session, model_cls, model_kwargs):
        with session.begin():
            model = model_cls(**model_kwargs)
            session.add(model)
        return model

    def create_listener(self, session, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID,
                  'id': self.FAKE_UUID,
                  'protocol': constants.PROTOCOL_HTTP,
                  'protocol_port': 80,
                  'provisioning_status': constants.ACTIVE,
                  'operating_status': constants.ONLINE,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.Listener, kwargs)

    def create_listener_statistics(self, session, listener_id, **overrides):
        kwargs = {'listener_id': listener_id,
                  'bytes_in': 0,
                  'bytes_out': 0,
                  'active_connections': 0,
                  'total_connections': 0}
        kwargs.update(overrides)
        return self._insert(session, models.ListenerStatistics, kwargs)

    def create_pool(self, session, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID,
                  'id': self.FAKE_UUID,
                  'protocol': constants.PROTOCOL_HTTP,
                  'lb_algorithm': constants.LB_ALGORITHM_ROUND_ROBIN,
                  'operating_status': constants.ONLINE,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.Pool, kwargs)

    def create_session_persistence(self, session, pool_id, **overrides):
        kwargs = {'pool_id': pool_id,
                  'type': constants.SESSION_PERSISTENCE_HTTP_COOKIE}
        kwargs.update(overrides)
        return self._insert(session, models.SessionPersistence, kwargs)

    def create_health_monitor(self, session, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID,
                  'id': self.FAKE_UUID,
                  'type': constants.HEALTH_MONITOR_HTTP,
                  'delay': 1,
                  'timeout': 1,
                  'max_retries': 1,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.HealthMonitor, kwargs)

    def create_member(self, session, pool_id, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID,
                  'id': self.FAKE_UUID,
                  'pool_id': pool_id,
                  'address': '10.0.0.1',
                  'protocol_port': 80,
                  'operating_status': constants.ONLINE,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.Member, kwargs)

    def create_load_balancer(self, session, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID,
                  'id': self.FAKE_UUID,
                  'vip_subnet_id': self.FAKE_UUID,
                  'provisioning_status': constants.ACTIVE,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.LoadBalancer, kwargs)


class PoolModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def test_create(self):
        self.create_pool(self.session)

    def test_update(self):
        pool = self.create_pool(self.session)
        id = pool.id
        pool.name = 'test1'
        new_pool = self.session.query(
            models.Pool).filter_by(id=id).first()
        self.assertEqual('test1', new_pool.name)

    def test_delete(self):
        pool = self.create_pool(self.session)
        id = pool.id
        with self.session.begin():
            self.session.delete(pool)
            self.session.flush()
        new_pool = self.session.query(
            models.Pool).filter_by(id=id).first()
        self.assertIsNone(new_pool)


class MemberModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def setUp(self):
        super(MemberModelTest, self).setUp()
        self.pool = self.create_pool(self.session)

    def test_create(self):
        self.create_member(self.session, self.pool.id)

    def test_update(self):
        member = self.create_member(self.session, self.pool.id)
        id = member.id
        member.name = 'test1'
        new_member = self.session.query(
            models.Member).filter_by(id=id).first()
        self.assertEqual('test1', new_member.name)

    def test_delete(self):
        member = self.create_member(self.session, self.pool.id)
        id = member.id
        with self.session.begin():
            self.session.delete(member)
            self.session.flush()
        new_member = self.session.query(
            models.Member).filter_by(id=id).first()
        self.assertIsNone(new_member)


class SessionPersistenceModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def setUp(self):
        super(SessionPersistenceModelTest, self).setUp()
        self.pool = self.create_pool(self.session)

    def test_create(self):
        self.create_session_persistence(self.session, self.pool.id)

    def test_update(self):
        session_persistence = self.create_session_persistence(self.session,
                                                              self.pool.id)
        session_persistence.name = 'test1'
        new_session_persistence = self.session.query(
            models.SessionPersistence).filter_by(pool_id=self.pool.id).first()
        self.assertEqual('test1', new_session_persistence.name)

    def test_delete(self):
        session_persistence = self.create_session_persistence(self.session,
                                                              self.pool.id)
        with self.session.begin():
            self.session.delete(session_persistence)
            self.session.flush()
        new_session_persistence = self.session.query(
            models.SessionPersistence).filter_by(pool_id=self.pool.id).first()
        self.assertIsNone(new_session_persistence)


class ListenerModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def test_create(self):
        self.create_listener(self.session)

    def test_update(self):
        listener = self.create_listener(self.session)
        id = listener.id
        listener.name = 'test1'
        new_listener = self.session.query(
            models.Listener).filter_by(id=id).first()
        self.assertEqual('test1', new_listener.name)

    def test_delete(self):
        listener = self.create_listener(self.session)
        id = listener.id
        with self.session.begin():
            self.session.delete(listener)
            self.session.flush()
        new_listener = self.session.query(
            models.Listener).filter_by(id=id).first()
        self.assertIsNone(new_listener)


class ListenerStatisticsModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def setUp(self):
        super(ListenerStatisticsModelTest, self).setUp()
        self.listener = self.create_listener(self.session)

    def test_create(self):
        self.create_listener_statistics(self.session, self.listener.id)

    def test_update(self):
        stats = self.create_listener_statistics(self.session, self.listener.id)
        stats.name = 'test1'
        new_stats = self.session.query(models.ListenerStatistics).filter_by(
            listener_id=self.listener.id).first()
        self.assertEqual('test1', new_stats.name)

    def test_delete(self):
        stats = self.create_listener_statistics(self.session, self.listener.id)
        with self.session.begin():
            self.session.delete(stats)
            self.session.flush()
        new_stats = self.session.query(models.ListenerStatistics).filter_by(
            listener_id=self.listener.id).first()
        self.assertIsNone(new_stats)


class HealthMonitorModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def test_create(self):
        self.create_health_monitor(self.session)

    def test_update(self):
        health_monitor = self.create_health_monitor(self.session)
        id = health_monitor.id
        health_monitor.name = 'test1'
        new_health_monitor = self.session.query(
            models.HealthMonitor).filter_by(id=id).first()
        self.assertEqual('test1', new_health_monitor.name)

    def test_delete(self):
        health_monitor = self.create_health_monitor(self.session)
        id = health_monitor.id
        with self.session.begin():
            self.session.delete(health_monitor)
            self.session.flush()
        new_health_monitor = self.session.query(
            models.HealthMonitor).filter_by(id=id).first()
        self.assertIsNone(new_health_monitor)


class LoadBalancerModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def test_create(self):
        self.create_load_balancer(self.session)

    def test_update(self):
        load_balancer = self.create_load_balancer(self.session)
        id = load_balancer.id
        load_balancer.name = 'test1'
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=id).first()
        self.assertEqual('test1', new_load_balancer.name)

    def test_delete(self):
        load_balancer = self.create_load_balancer(self.session)
        id = load_balancer.id
        with self.session.begin():
            self.session.delete(load_balancer)
            self.session.flush()
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=id).first()
        self.assertIsNone(new_load_balancer)