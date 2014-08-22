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

from octavia.common import constants
from octavia.common import data_models
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

    def associate_container(self, load_balancer, container):
        load_balancer.containers.append(container)

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
                  'operating_status': constants.ONLINE,
                  'enabled': True}
        kwargs.update(overrides)
        return self._insert(session, models.LoadBalancer, kwargs)

    def create_sni(self, session, **overrides):
        kwargs = {'listener_id': self.FAKE_UUID_1,
                  'tls_container_id': self.FAKE_UUID_1}
        kwargs.update(overrides)
        return self._insert(session, models.SNI, kwargs)

    def create_container(self, session, **overrides):
        kwargs = {'id': self.FAKE_UUID_1,
                  'host_id': self.FAKE_UUID_1,
                  'status': constants.ONLINE}
        kwargs.update(overrides)
        return self._insert(session, models.Container, kwargs)


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
        member_id = member.id
        member.name = 'test1'
        new_member = self.session.query(
            models.Member).filter_by(id=member_id).first()
        self.assertEqual('test1', new_member.name)

    def test_delete(self):
        member = self.create_member(self.session, self.pool.id)
        member_id = member.id
        with self.session.begin():
            self.session.delete(member)
            self.session.flush()
        new_member = self.session.query(
            models.Member).filter_by(id=member_id).first()
        self.assertIsNone(new_member)

    def test_pool_relationship(self):
        member = self.create_member(self.session, self.pool.id,
                                    id=self.FAKE_UUID_1,
                                    address="10.0.0.1")
        self.create_member(self.session, self.pool.id, id=self.FAKE_UUID_2,
                           address="10.0.0.2")
        new_member = self.session.query(models.Member).filter_by(
            id=member.id).first()
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
        listener_id = listener.id
        listener.name = 'test1'
        new_listener = self.session.query(
            models.Listener).filter_by(id=listener_id).first()
        self.assertEqual('test1', new_listener.name)

    def test_delete(self):
        listener = self.create_listener(self.session)
        listener_id = listener.id
        with self.session.begin():
            self.session.delete(listener)
            self.session.flush()
        new_listener = self.session.query(
            models.Listener).filter_by(id=listener_id).first()
        self.assertIsNone(new_listener)

    def test_load_balancer_relationship(self):
        lb = self.create_load_balancer(self.session)
        listener = self.create_listener(self.session, load_balancer_id=lb.id)
        new_listener = self.session.query(
            models.Listener).filter_by(id=listener.id).first()
        self.assertIsNotNone(new_listener.load_balancer)
        self.assertTrue(isinstance(new_listener.load_balancer,
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

    def test_sni_relationship(self):
        listener = self.create_listener(self.session)
        self.create_sni(self.session, listener_id=listener.id,
                        tls_container_id=self.FAKE_UUID_1)
        self.create_sni(self.session, listener_id=listener.id,
                        tls_container_id=self.FAKE_UUID_2)
        new_listener = self.session.query(models.Listener).filter_by(
            id=listener.id).first()
        self.assertIsNotNone(new_listener.sni_containers)
        self.assertEqual(2, len(new_listener.sni_containers))


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
        health_monitor_id = health_monitor.id
        health_monitor.name = 'test1'
        new_health_monitor = self.session.query(
            models.HealthMonitor).filter_by(id=health_monitor_id).first()
        self.assertEqual('test1', new_health_monitor.name)

    def test_delete(self):
        health_monitor = self.create_health_monitor(self.session)
        health_monitor_id = health_monitor.id
        with self.session.begin():
            self.session.delete(health_monitor)
            self.session.flush()
        new_health_monitor = self.session.query(
            models.HealthMonitor).filter_by(id=health_monitor_id).first()
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
        lb_id = load_balancer.id
        load_balancer.name = 'test1'
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=lb_id).first()
        self.assertEqual('test1', new_load_balancer.name)

    def test_delete(self):
        load_balancer = self.create_load_balancer(self.session)
        lb_id = load_balancer.id
        with self.session.begin():
            self.session.delete(load_balancer)
            self.session.flush()
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=lb_id).first()
        self.assertIsNone(new_load_balancer)

    def test_listener_relationship(self):
        load_balancer = self.create_load_balancer(self.session)
        self.create_listener(self.session, load_balancer_id=load_balancer.id)
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=load_balancer.id).first()
        self.assertIsNotNone(new_load_balancer.listeners)
        self.assertEqual(1, len(new_load_balancer.listeners))

    def test_load_balancer_container_relationship(self):
        load_balancer = self.create_load_balancer(self.session)
        container = self.create_container(self.session)
        self.associate_container(load_balancer, container)
        new_load_balancer = self.session.query(
            models.LoadBalancer).filter_by(id=load_balancer.id).first()
        self.assertIsNotNone(new_load_balancer.containers)
        self.assertEqual(1, len(new_load_balancer.containers))


class SNIModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def setUp(self):
        super(SNIModelTest, self).setUp()
        self.listener = self.create_listener(self.session)

    def test_create(self):
        self.create_sni(self.session)

    def test_update(self):
        sni = self.create_sni(self.session, listener_id=self.listener.id)
        sni.listener_id = self.FAKE_UUID_2
        new_sni = self.session.query(
            models.SNI).filter_by(listener_id=self.FAKE_UUID_2).first()
        self.assertEqual(self.FAKE_UUID_2, new_sni.listener_id)

    def test_delete(self):
        sni = self.create_sni(self.session, listener_id=self.listener.id)
        with self.session.begin():
            self.session.delete(sni)
            self.session.flush()
        new_sni = self.session.query(
            models.SNI).filter_by(listener_id=self.listener.id).first()
        self.assertIsNone(new_sni)

    def test_sni_relationship(self):
        self.create_sni(self.session, listener_id=self.listener.id)
        new_sni = self.session.query(models.SNI).filter_by(
            listener_id=self.listener.id).first()
        self.assertIsNotNone(new_sni.listener)
        self.assertTrue(isinstance(new_sni.listener, models.Listener))


class ContainerModelTest(base.OctaviaDBTestBase, ModelTestMixin):

    def setUp(self):
        super(ContainerModelTest, self).setUp()
        self.load_balancer = self.create_load_balancer(self.session)

    def test_create(self):
        self.create_container(self.session)

    def test_update(self):
        container = self.create_container(
            self.session)
        container.container_id = self.FAKE_UUID_2
        new_container = self.session.query(models.Container).filter_by(
            id=container.id).first()
        self.assertEqual(self.FAKE_UUID_2, new_container.container_id)

    def test_delete(self):
        container = self.create_container(
            self.session)
        with self.session.begin():
            self.session.delete(container)
            self.session.flush()
        new_container = self.session.query(
            models.Container).filter_by(id=container.id).first()
        self.assertIsNone(new_container)

    def test_load_balancer_relationship(self):
        container = self.create_container(self.session)
        self.associate_container(self.load_balancer, container)
        new_container = self.session.query(models.Container).filter_by(
            id=container.id).first()
        self.assertIsNotNone(new_container.load_balancers)
        self.assertTrue(isinstance(new_container.load_balancers, list))
        self.assertTrue(1, len(new_container.load_balancers))


class DataModelConversionTest(base.OctaviaDBTestBase, ModelTestMixin):

    def setUp(self):
        super(DataModelConversionTest, self).setUp()
        self.hm = self.create_health_monitor(self.session)
        self.pool = self.create_pool(self.session,
                                     health_monitor_id=self.hm.id)
        self.member = self.create_member(self.session, self.pool.id,
                                         id=self.FAKE_UUID_1,
                                         address='10.0.0.1')
        self.sp = self.create_session_persistence(self.session, self.pool.id)
        self.lb = self.create_load_balancer(self.session)
        self.listener = self.create_listener(self.session,
                                             default_pool_id=self.pool.id,
                                             load_balancer_id=self.lb.id)
        self.stats = self.create_listener_statistics(self.session,
                                                     self.listener.id)
        self.sni = self.create_sni(self.session, listener_id=self.listener.id)

    def test_load_balancer_tree(self):
        lb_db = self.session.query(models.LoadBalancer).filter_by(
            id=self.lb.id).first()
        self.check_load_balancer(lb_db.to_data_model())

    def test_listener_tree(self):
        listener_db = self.session.query(models.Listener).filter_by(
            id=self.listener.id).first()
        self.check_listener(listener_db.to_data_model())

    def test_sni_tree(self):
        sni_db = self.session.query(models.SNI).filter_by(
            listener_id=self.listener.id).first()
        self.check_sni(sni_db.to_data_model())

    def test_listener_statistics_tree(self):
        stats_db = self.session.query(models.ListenerStatistics).filter_by(
            listener_id=self.listener.id).first()
        self.check_listener_statistics(stats_db.to_data_model())

    def test_pool_tree(self):
        pool_db = self.session.query(models.Pool).filter_by(
            id=self.pool.id).first()
        self.check_pool(pool_db.to_data_model())

    def test_session_persistence_tree(self):
        sp_db = self.session.query(models.SessionPersistence).filter_by(
            pool_id=self.pool.id).first()
        self.check_session_persistence(sp_db.to_data_model())

    def test_health_monitor_tree(self):
        hm_db = self.session.query(models.HealthMonitor).filter_by(
            id=self.hm.id).first()
        self.check_health_monitor(hm_db.to_data_model())

    def test_member_tree(self):
        member_db = self.session.query(models.Member).filter_by(
            id=self.member.id).first()
        self.check_member(member_db.to_data_model())

    def check_load_balancer(self, lb, check_listeners=True,
                            check_containers=True):
        self.assertIsInstance(lb, data_models.LoadBalancer)
        self.check_load_balancer_data_model(lb)
        self.assertIsInstance(lb.listeners, list)
        self.assertIsInstance(lb.containers, list)
        if check_listeners:
            for listener in lb.listeners:
                self.check_listener(listener, check_lb=False)
        if check_containers:
            for container in lb.containers:
                self.check_container(container, check_load_balancers=False)

    def check_sni(self, sni, check_listener=True):
        self.assertIsInstance(sni, data_models.SNI)
        self.check_sni_data_model(sni)
        if check_listener:
            self.check_listener(sni.listener, check_sni=False)

    def check_listener_statistics(self, stats, check_listener=True):
        self.assertIsInstance(stats, data_models.ListenerStatistics)
        self.check_listener_statistics_data_model(stats)
        if check_listener:
            self.check_listener(stats.listener, check_statistics=False)

    def check_container(self, container, check_load_balancers=True):
        self.assertIsInstance(container, data_models.Container)
        self.check_container_data_model(container)
        if check_load_balancers:
            for load_balancer in container.load_balancers:
                self.check_load_balancer(load_balancer)

    def check_listener(self, listener, check_sni=True, check_pool=True,
                       check_lb=True, check_statistics=True):
        self.assertIsInstance(listener, data_models.Listener)
        self.check_listener_data_model(listener)
        if check_lb:
            self.check_load_balancer(listener.load_balancer)
        if check_sni:
            c_containers = listener.sni_containers
            self.assertIsInstance(c_containers, list)
            for sni in c_containers:
                self.check_sni(sni, check_listener=False)
        if check_pool:
            self.check_pool(listener.default_pool, check_listener=False)
        if check_statistics:
            self.check_listener_statistics(listener.stats,
                                           check_listener=False)

    def check_session_persistence(self, session_persistence, check_pool=True):
        self.assertIsInstance(session_persistence,
                              data_models.SessionPersistence)
        self.check_session_persistence_data_model(session_persistence)
        if check_pool:
            self.check_pool(session_persistence.pool, check_sp=False)

    def check_member(self, member, check_pool=True):
        self.assertIsInstance(member, data_models.Member)
        self.check_member_data_model(member)
        if check_pool:
            self.check_pool(member.pool)

    def check_health_monitor(self, health_monitor, check_pool=True):
        self.assertIsInstance(health_monitor, data_models.HealthMonitor)
        self.check_health_monitor_data_model(health_monitor)
        if check_pool:
            self.check_pool(health_monitor.pool, check_hm=False)

    def check_pool(self, pool, check_listener=True, check_sp=True,
                   check_hm=True, check_members=True):
        self.assertIsInstance(pool, data_models.Pool)
        self.check_pool_data_model(pool)
        if check_listener:
            self.check_listener(pool.listener, check_pool=False)
        if check_sp:
            self.check_session_persistence(pool.session_persistence,
                                           check_pool=False)
        if check_members:
            c_members = pool.members
            self.assertIsNotNone(c_members)
            self.assertEqual(1, len(c_members))
            for c_member in c_members:
                self.check_member(c_member, check_pool=False)
        if check_hm:
            self.check_health_monitor(pool.health_monitor, check_pool=False)

    def check_load_balancer_data_model(self, lb):
        self.assertEqual(self.FAKE_UUID_1, lb.tenant_id)
        self.assertEqual(self.FAKE_UUID_1, lb.id)
        self.assertEqual(self.FAKE_UUID_1, lb.vip_subnet_id)
        self.assertEqual(constants.ACTIVE, lb.provisioning_status)
        self.assertEqual(True, lb.enabled)

    def check_listener_data_model(self, listener):
        self.assertEqual(self.FAKE_UUID_1, listener.tenant_id)
        self.assertEqual(self.FAKE_UUID_1, listener.id)
        self.assertEqual(constants.PROTOCOL_HTTP, listener.protocol)
        self.assertEqual(80, listener.protocol_port)
        self.assertEqual(constants.ACTIVE, listener.provisioning_status)
        self.assertEqual(constants.ONLINE, listener.operating_status)
        self.assertEqual(True, listener.enabled)

    def check_sni_data_model(self, sni):
        self.assertEqual(self.FAKE_UUID_1, sni.listener_id)
        self.assertEqual(self.FAKE_UUID_1, sni.tls_container_id)

    def check_listener_statistics_data_model(self, stats):
        self.assertEqual(self.listener.id, stats.listener_id)
        self.assertEqual(0, stats.bytes_in)
        self.assertEqual(0, stats.bytes_out)
        self.assertEqual(0, stats.active_connections)
        self.assertEqual(0, stats.total_connections)

    def check_pool_data_model(self, pool):
        self.assertEqual(self.FAKE_UUID_1, pool.tenant_id)
        self.assertEqual(self.FAKE_UUID_1, pool.id)
        self.assertEqual(constants.PROTOCOL_HTTP, pool.protocol)
        self.assertEqual(constants.LB_ALGORITHM_ROUND_ROBIN, pool.lb_algorithm)
        self.assertEqual(constants.ONLINE, pool.operating_status)
        self.assertEqual(True, pool.enabled)

    def check_session_persistence_data_model(self, sp):
        self.assertEqual(self.pool.id, sp.pool_id)
        self.assertEqual(constants.SESSION_PERSISTENCE_HTTP_COOKIE, sp.type)

    def check_health_monitor_data_model(self, hm):
        self.assertEqual(self.FAKE_UUID_1, hm.tenant_id)
        self.assertEqual(self.FAKE_UUID_1, hm.id)
        self.assertEqual(constants.HEALTH_MONITOR_HTTP, hm.type)
        self.assertEqual(1, hm.delay)
        self.assertEqual(1, hm.timeout)
        self.assertEqual(1, hm.max_retries)
        self.assertEqual(True, hm.enabled)

    def check_member_data_model(self, member):
        self.assertEqual(self.FAKE_UUID_1, member.tenant_id)
        self.assertEqual(self.FAKE_UUID_1, member.id)
        self.assertEqual(self.pool.id, member.pool_id)
        self.assertEqual('10.0.0.1', member.address)
        self.assertEqual(80, member.protocol_port)
        self.assertEqual(constants.ONLINE, member.operating_status)
        self.assertEqual(True, member.enabled)

    def check_container_data_model(self, container):
        self.assertEqual(self.FAKE_UUID_1, container.id)
        self.assertEqual(self.FAKE_UUID_1, container.host_id)
        self.assertEqual(constants.ONLINE, container.status)

    def check_load_balancer_container_data_model(self, container):
        self.assertEqual(self.FAKE_UUID_1, container.container_id)
        self.assertEqual(self.FAKE_UUID_1, container.load_balancer_id)
