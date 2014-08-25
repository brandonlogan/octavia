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

    FAKE_UUID_1 = '0123456789012345678901234567890123456'
    FAKE_UUID_2 = '1234567890123456789012345678901234567'

    def _insert(self, session, model_cls, model_kwargs):
        with session.begin():
            model = model_cls(**model_kwargs)
            session.add(model)
        return model

    def create_listener(self, session, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID_1,
                  'id': self.FAKE_UUID_1,
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
        kwargs = {'tenant_id': self.FAKE_UUID_1,
                  'id': self.FAKE_UUID_1,
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
        kwargs = {'tenant_id': self.FAKE_UUID_1,
                  'id': self.FAKE_UUID_1,
                  'type': constants.HEALTH_MONITOR_HTTP,
                  'delay': 1,
                  'timeout': 1,
                  'max_retries': 1,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.HealthMonitor, kwargs)

    def create_member(self, session, pool_id, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID_1,
                  'id': self.FAKE_UUID_1,
                  'pool_id': pool_id,
                  'address': '10.0.0.1',
                  'protocol_port': 80,
                  'operating_status': constants.ONLINE,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.Member, kwargs)

    def create_load_balancer(self, session, **overrides):
        kwargs = {'tenant_id': self.FAKE_UUID_1,
                  'id': self.FAKE_UUID_1,
                  'vip_subnet_id': self.FAKE_UUID_1,
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

    def test_member_relationship(self):
        pool = self.create_pool(self.session)
        self.create_member(self.session, pool.id, id=self.FAKE_UUID_1,
                           address="10.0.0.1")
        self.create_member(self.session, pool.id, id=self.FAKE_UUID_2,
                           address="10.0.0.2")
        new_pool = self.session.query(
            models.Pool).filter_by(id=pool.id).first()
        self.assertIsNotNone(new_pool.members)
        self.assertEqual(2, len(new_pool.members))
        self.assertTrue(isinstance(new_pool.members[0], models.Member))

    def test_health_monitor_relationship(self):
        hm = self.create_health_monitor(self.session)
        pool = self.create_pool(self.session, health_monitor_id=hm.id)
        new_pool = self.session.query(models.Pool).filter_by(
            id=pool.id).first()
        self.assertIsNotNone(new_pool.health_monitor)
        self.assertTrue(isinstance(new_pool.health_monitor,
                                   models.HealthMonitor))

    def test_session_persistence_relationship(self):
        pool = self.create_pool(self.session)
        self.create_session_persistence(self.session, pool_id=pool.id)
        new_pool = self.session.query(models.Pool).filter_by(
            id=pool.id).first()
        self.assertIsNotNone(new_pool.session_persistence)
        self.assertTrue(isinstance(new_pool.session_persistence,
                                   models.SessionPersistence))

    def test_listener_relationship(self):
        pool = self.create_pool(self.session)
        self.create_listener(self.session, default_pool_id=pool.id)
        new_pool = self.session.query(models.Pool).filter_by(
            id=pool.id).first()
        self.assertIsNotNone(new_pool.listener)
        self.assertTrue(isinstance(new_pool.listener, models.Listener))


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

    def test_pool_relationship(self):
        member1 = self.create_member(self.session, self.pool.id,
                                     id=self.FAKE_UUID_1,
                                     address="10.0.0.1")
        self.create_member(self.session, self.pool.id, id=self.FAKE_UUID_2,
                           address="10.0.0.2")
        new_member = self.session.query(models.Member).filter_by(
            id=member1.id).first()
        self.assertIsNotNone(new_member.pool)
        self.assertTrue(isinstance(new_member.pool, models.Pool))


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

    def test_pool_relationship(self):
        self.create_session_persistence(self.session, self.pool.id)
        new_persistence = self.session.query(
            models.SessionPersistence).filter_by(pool_id=self.pool.id).first()
        self.assertIsNotNone(new_persistence.pool)
        self.assertTrue(isinstance(new_persistence.pool, models.Pool))


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

    def test_load_balancer_relationship(self):
        lb = self.create_load_balancer(self.session)
        listener = self.create_listener(self.session, load_balancer_id=lb.id)
        self.assertIsNotNone(listener.load_balancer)
        self.assertTrue(isinstance(listener.load_balancer,
                                   models.LoadBalancer))

    def test_listener_statistics_relationship(self):
        listener = self.create_listener(self.session)
        self.create_listener_statistics(self.session, listener_id=listener.id)
        new_listener = self.session.query(models.Listener).filter_by(
            id=listener.id).first()
        self.assertIsNotNone(new_listener.stats)
        self.assertTrue(isinstance(new_listener.stats,
                                   models.ListenerStatistics))

    def test_pool_relationship(self):
        pool = self.create_pool(self.session)
        listener = self.create_listener(self.session, default_pool_id=pool.id)
        new_listener = self.session.query(models.Listener).filter_by(
            id=listener.id).first()
        self.assertIsNotNone(new_listener.default_pool)
        self.assertTrue(isinstance(new_listener.default_pool, models.Pool))


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

    def test_listener_relationship(self):
        self.create_listener_statistics(self.session, self.listener.id)
        new_stats = self.session.query(models.ListenerStatistics).filter_by(
            listener_id=self.listener.id).first()
        self.assertIsNotNone(new_stats.listener)
        self.assertTrue(isinstance(new_stats.listener, models.Listener))


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

    def test_pool_relationship(self):
        health_monitor = self.create_health_monitor(self.session)
        self.create_pool(self.session, health_monitor_id=health_monitor.id)
        new_health_monitor = self.session.query(
            models.HealthMonitor).filter_by(id=health_monitor.id).first()
        self.assertIsNotNone(new_health_monitor.pool)
        self.assertTrue(isinstance(new_health_monitor.pool, models.Pool))


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

    def test_listener_relationship(self):
        load_balancer = self.create_load_balancer(self.session)
        self.create_listener(self.session, load_balancer_id=load_balancer.id)
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=load_balancer.id).first()
        self.assertIsNotNone(new_load_balancer.listeners)
        self.assertTrue(len(new_load_balancer.listeners) > 0)


class DataModelConversionTest(base.OctaviaDBTestBase, ModelTestMixin):

    def test_full_tree(self):
        hm = self.create_health_monitor(self.session)
        hm_dm = hm.to_data_model()
        pool = self.create_pool(self.session, health_monitor_id=hm.id)
        pool_dm = pool.to_data_model()
        member1 = self.create_member(self.session, pool.id,
                                     id=self.FAKE_UUID_1, address='10.0.0.1')
        member1_dm = member1.to_data_model()
        member2 = self.create_member(self.session, pool.id,
                                     id=self.FAKE_UUID_2, address='10.0.0.2')
        member2_dm = member2.to_data_model()
        sp = self.create_session_persistence(self.session, pool.id)
        sp_dm = sp.to_data_model()
        lb = self.create_load_balancer(self.session)
        lb_dm = lb.to_data_model
        listener = self.create_listener(self.session, default_pool_id=pool.id,
                                        load_balancer_id=lb.id)
        listener_dm = listener.to_data_model()
        stats = self.create_listener_statistics(self.session, listener.id)
        stats_dm = stats.to_data_model()
        db_lb = self.session.query(
            models.LoadBalancer).filter_by(id=lb.id).first()
        db_lb_dm = db_lb.to_data_model()
        self.assertIsNotNone(db_lb_dm)
        self.assertIsNotNone(db_lb_dm.listeners)
        self.assertEqual(1, len(db_lb_dm.listeners))