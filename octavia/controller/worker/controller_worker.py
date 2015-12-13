# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import logging

from octavia.common import base_taskflow
from octavia.common import constants
from octavia.controller.worker.flows import amphora_flows
from octavia.controller.worker.flows import health_monitor_flows
from octavia.controller.worker.flows import listener_flows
from octavia.controller.worker.flows import load_balancer_flows
from octavia.controller.worker.flows import member_flows
from octavia.controller.worker.flows import pool_flows
from octavia.db import api as db_apis
from octavia.db import repositories as repo
from octavia.i18n import _LI

from oslo_config import cfg
from taskflow.listeners import logging as tf_logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class ControllerWorker(base_taskflow.BaseTaskFlowEngine):

    def __init__(self):

        self._amphora_flows = amphora_flows.AmphoraFlows()
        self._health_monitor_flows = health_monitor_flows.HealthMonitorFlows()
        self._lb_flows = load_balancer_flows.LoadBalancerFlows()
        self._listener_flows = listener_flows.ListenerFlows()
        self._member_flows = member_flows.MemberFlows()
        self._pool_flows = pool_flows.PoolFlows()

        self._amphora_repo = repo.AmphoraRepository()
        self._health_mon_repo = repo.HealthMonitorRepository()
        self._lb_repo = repo.LoadBalancerRepository()
        self._listener_repo = repo.ListenerRepository()
        self._member_repo = repo.MemberRepository()
        self._pool_repo = repo.PoolRepository()

        super(ControllerWorker, self).__init__()

    def create_amphora(self):
        """Creates an Amphora.

        :returns: amphora_id
        """
        create_amp_tf = self._taskflow_load(self._amphora_flows.
                                            get_create_amphora_flow())
        with tf_logging.DynamicLoggingListener(create_amp_tf,
                                               log=LOG):
            create_amp_tf.run()

        return create_amp_tf.storage.fetch('amphora')

    def delete_amphora(self, amphora_id):
        """Deletes an existing Amphora.

        :param amphora_id: ID of the amphora to delete
        :returns: None
        :raises AmphoraNotFound: The referenced Amphora was not found
        """
        amphora = self._amphora_repo.get(db_apis.get_session(),
                                         id=amphora_id)
        delete_amp_tf = self._taskflow_load(self._amphora_flows.
                                            get_delete_amphora_flow(),
                                            store={constants.AMPHORA: amphora})
        with tf_logging.DynamicLoggingListener(delete_amp_tf,
                                               log=LOG):
            delete_amp_tf.run()

    def create_health_monitor(self, pool_id):
        """Creates a health monitor.

        :param pool_id: ID of the pool to create a health monitor on
        :returns: None
        :raises NoSuitablePool: Unable to find the node pool
        """
        health_mon = self._health_mon_repo.get(db_apis.get_session(),
                                               pool_id=pool_id)

        listener = health_mon.pool.listener
        health_mon.pool.health_monitor = health_mon
        listener.default_pool = health_mon.pool
        vip = health_mon.pool.listener.load_balancer.vip
        load_balancer = health_mon.pool.listener.load_balancer

        create_hm_tf = self._taskflow_load(self._health_monitor_flows.
                                           get_create_health_monitor_flow(),
                                           store={constants.HEALTH_MON:
                                                  health_mon,
                                                  constants.LISTENER: listener,
                                                  constants.LOADBALANCER:
                                                      load_balancer,
                                                  constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(create_hm_tf,
                                               log=LOG):
            create_hm_tf.run()

    def delete_health_monitor(self, pool_id):
        """Deletes a health monitor.

        :param pool_id: ID of the pool to delete its health monitor
        :returns: None
        :raises HMNotFound: The referenced health monitor was not found
        """
        health_mon = self._health_mon_repo.get(db_apis.get_session(),
                                               pool_id=pool_id)

        listener = health_mon.pool.listener
        listener.default_pool = health_mon.pool
        vip = listener.load_balancer.vip
        load_balancer = listener.load_balancer

        delete_hm_tf = self._taskflow_load(
            self._health_monitor_flows.get_delete_health_monitor_flow(),
            store={constants.HEALTH_MON: health_mon, constants.POOL_ID:
                   pool_id, constants.LISTENER: listener,
                   constants.LOADBALANCER: load_balancer, constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(delete_hm_tf,
                                               log=LOG):
            delete_hm_tf.run()

    def update_health_monitor(self, pool_id, health_monitor_updates):
        """Updates a health monitor.

        :param pool_id: ID of the pool to have it's health monitor updated
        :param health_monitor_updates: Dict containing updated health monitor
        :returns: None
        :raises HMNotFound: The referenced health monitor was not found
        """
        health_mon = self._health_mon_repo.get(db_apis.get_session(),
                                               pool_id=pool_id)

        listener = health_mon.pool.listener
        health_mon.pool.health_monitor = health_mon
        listener.default_pool = health_mon.pool
        vip = health_mon.pool.listener.load_balancer.vip
        load_balancer = health_mon.pool.listener.load_balancer

        update_hm_tf = self._taskflow_load(self._health_monitor_flows.
                                           get_update_health_monitor_flow(),
                                           store={constants.HEALTH_MON:
                                                  health_mon,
                                                  constants.LISTENER: listener,
                                                  constants.LOADBALANCER:
                                                      load_balancer,
                                                  constants.VIP: vip,
                                                  constants.UPDATE_DICT:
                                                      health_monitor_updates})
        with tf_logging.DynamicLoggingListener(update_hm_tf,
                                               log=LOG):
            update_hm_tf.run()

    def create_listener(self, listener_id, full_tree=False):
        """Creates a listener.

        :param listener_id: ID of the listener to create
        :param full_tree: boolean of whether this is part of a full lb tree
                          creation request
        :returns: None
        :raises NoSuitableLB: Unable to find the load balancer
        """
        listener = self._listener_repo.get(db_apis.get_session(),
                                           id=listener_id)
        load_balancer = listener.load_balancer
        vip = listener.load_balancer.vip

        create_listener_tf = self._taskflow_load(
            self._listener_flows.get_create_listener_flow(full_tree=full_tree),
            store={constants.LISTENER: listener,
                   constants.LOADBALANCER: load_balancer,
                   constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(create_listener_tf, log=LOG):
            create_listener_tf.run()

    def delete_listener(self, listener_id):
        """Deletes a listener.

        :param listener_id: ID of the listener to delete
        :returns: None
        :raises ListenerNotFound: The referenced listener was not found
        """
        listener = self._listener_repo.get(db_apis.get_session(),
                                           id=listener_id)
        load_balancer = listener.load_balancer
        vip = load_balancer.vip

        delete_listener_tf = self._taskflow_load(
            self._listener_flows.get_delete_listener_flow(),
            store={constants.LOADBALANCER: load_balancer,
                   constants.LISTENER: listener, constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(delete_listener_tf,
                                               log=LOG):
            delete_listener_tf.run()

    def update_listener(self, listener_id, listener_updates):
        """Updates a listener.

        :param listener_id: ID of the listener to update
        :param listener_updates: Dict containing updated listener attributes
        :returns: None
        :raises ListenerNotFound: The referenced listener was not found
        """
        listener = self._listener_repo.get(db_apis.get_session(),
                                           id=listener_id)

        load_balancer = listener.load_balancer
        vip = listener.load_balancer.vip

        update_listener_tf = self._taskflow_load(self._listener_flows.
                                                 get_update_listener_flow(),
                                                 store={constants.LISTENER:
                                                        listener,
                                                        constants.VIP: vip,
                                                        constants.LOADBALANCER:
                                                            load_balancer,
                                                        constants.UPDATE_DICT:
                                                            listener_updates})
        with tf_logging.DynamicLoggingListener(update_listener_tf, log=LOG):
            update_listener_tf.run()

    def _create_load_balancer_tree(self, store, load_balancer):
        topology = CONF.controller_worker.loadbalancer_topology
        create_lb_tf = self._taskflow_load(
            self._lb_flows.get_create_load_balancer_flow(topology=topology),
            store=store)
        with tf_logging.DynamicLoggingListener(create_lb_tf, log=LOG):
            create_lb_tf.run()
            # Ideally the following flow should be integrated with the
            # create_active_standby flow. This is not possible with the
            # current version of taskflow as it flatten out the flows.
            # Bug report: https://bugs.launchpad.net/taskflow/+bug/1479466
            post_lb_amp_assoc = self._taskflow_load(
                self._lb_flows.get_post_lb_amp_association_flow(
                    prefix='post-amphora-association',
                    topology=CONF.controller_worker.loadbalancer_topology,
                    full_tree=True),
                store=store)
            with tf_logging.DynamicLoggingListener(post_lb_amp_assoc, log=LOG):
                post_lb_amp_assoc.run()
            # NOTE(blogan): This is not calling the pool or health monitor
            # creates because calling just create_listener will update the
            # haproxy config with everything already in the db.  The member
            # create is being called for the network plugging it does.
            for listener in load_balancer.listeners:
                self.create_listener(listener.id, full_tree=True)
                if listener.default_pool:
                    for member in listener.default_pool.members:
                        self.create_member(member.id, full_tree=True)
            lb_tree_finalize = self._taskflow_load(
                self._lb_flows.get_full_tree_load_balancer_finalize_flow(),
                store={constants.LOADBALANCER: load_balancer})
            with tf_logging.DynamicLoggingListener(lb_tree_finalize, log=LOG):
                lb_tree_finalize.run()

    def create_load_balancer(self, load_balancer_id):
        """Creates a load balancer by allocating Amphorae.

        First tries to allocate an existing Amphora in READY state.
        If none are available it will attempt to build one specificly
        for this load balancer.

        :param load_balancer_id: ID of the load balancer to create
        :returns: None
        :raises NoSuitableAmphoraException: Unable to allocate an Amphora.
        """

        # Note this is a bit strange in how it handles building
        # Amphora if there are no spares.  TaskFlow has a spec for
        # a conditional flow that would make this cleaner once implemented.
        # https://review.openstack.org/#/c/98946/

        store = {constants.LOADBALANCER_ID: load_balancer_id}

        topology = CONF.controller_worker.loadbalancer_topology

        if topology == constants.TOPOLOGY_SINGLE:
            store[constants.UPDATE_DICT] = {constants.LOADBALANCER_TOPOLOGY:
                                            constants.TOPOLOGY_SINGLE}
        elif topology == constants.TOPOLOGY_ACTIVE_STANDBY:
            store[constants.UPDATE_DICT] = {constants.LOADBALANCER_TOPOLOGY:
                                            constants.TOPOLOGY_ACTIVE_STANDBY}
        # blogan and sbalukoff asked to remove the else check here
        # as it is also checked later in the flow create code

        lb = self._lb_repo.get(db_apis.get_session(), id=load_balancer_id)
        # if listeners exist then this was a request to create many resources
        # at once, so different logic will be needed.
        if lb.listeners:
            self._create_load_balancer_tree(store, lb)
            return

        create_lb_tf = self._taskflow_load(
            self._lb_flows.get_create_load_balancer_flow(topology=topology),
            store=store)
        with tf_logging.DynamicLoggingListener(create_lb_tf, log=LOG):
            create_lb_tf.run()
            # Ideally the following flow should be integrated with the
            # create_active_standby flow. This is not possible with the
            # current version of taskflow as it flatten out the flows.
            # Bug report: https://bugs.launchpad.net/taskflow/+bug/1479466
            post_lb_amp_assoc = self._taskflow_load(
                self._lb_flows.get_post_lb_amp_association_flow(
                    prefix='post-amphora-association',
                    topology=CONF.controller_worker.loadbalancer_topology),
                store=store)
            with tf_logging.DynamicLoggingListener(post_lb_amp_assoc, log=LOG):
                post_lb_amp_assoc.run()

    def delete_load_balancer(self, load_balancer_id):
        """Deletes a load balancer by de-allocating Amphorae.

        :param load_balancer_id: ID of the load balancer to delete
        :returns: None
        :raises LBNotFound: The referenced load balancer was not found
        """
        lb = self._lb_repo.get(db_apis.get_session(),
                               id=load_balancer_id)

        delete_lb_tf = self._taskflow_load(self._lb_flows.
                                           get_delete_load_balancer_flow(),
                                           store={constants.LOADBALANCER: lb})

        with tf_logging.DynamicLoggingListener(delete_lb_tf,
                                               log=LOG):
            delete_lb_tf.run()

    def update_load_balancer(self, load_balancer_id, load_balancer_updates):
        """Updates a load balancer.

        :param load_balancer_id: ID of the load balancer to update
        :param load_balancer_updates: Dict containing updated load balancer
        :returns: None
        :raises LBNotFound: The referenced load balancer was not found
        """
        lb = self._lb_repo.get(db_apis.get_session(),
                               id=load_balancer_id)

        update_lb_tf = self._taskflow_load(
            self._lb_flows.get_update_load_balancer_flow(),
            store={constants.LOADBALANCER: lb,
                   constants.UPDATE_DICT: load_balancer_updates})

        with tf_logging.DynamicLoggingListener(update_lb_tf,
                                               log=LOG):
            update_lb_tf.run()

    def create_member(self, member_id, full_tree=False):
        """Creates a pool member.

        :param member_id: ID of the member to create
        :param full_tree: boolean of whether this is part of a full lb tree
                          creation request
        :returns: None
        :raises NoSuitablePool: Unable to find the node pool
        """
        member = self._member_repo.get(db_apis.get_session(),
                                       id=member_id)

        listener = member.pool.listener
        listener.default_pool = member.pool
        load_balancer = listener.load_balancer
        vip = listener.load_balancer.vip

        create_member_tf = self._taskflow_load(
            self._member_flows.get_create_member_flow(full_tree=full_tree),
            store={constants.MEMBER: member, constants.LISTENER: listener,
                   constants.LOADBALANCER: load_balancer, constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(create_member_tf, log=LOG):
            create_member_tf.run()

    def delete_member(self, member_id):
        """Deletes a pool member.

        :param member_id: ID of the member to delete
        :returns: None
        :raises MemberNotFound: The referenced member was not found
        """
        member = self._member_repo.get(db_apis.get_session(),
                                       id=member_id)

        listener = member.pool.listener
        listener.default_pool = member.pool
        load_balancer = listener.load_balancer
        vip = load_balancer.vip

        delete_member_tf = self._taskflow_load(
            self._member_flows.get_delete_member_flow(),
            store={constants.MEMBER: member, constants.MEMBER_ID: member_id,
                   constants.LISTENER: listener, constants.VIP: vip,
                   constants.LOADBALANCER: load_balancer})
        with tf_logging.DynamicLoggingListener(delete_member_tf,
                                               log=LOG):
            delete_member_tf.run()

    def update_member(self, member_id, member_updates):
        """Updates a pool member.

        :param member_id: ID of the member to update
        :param member_updates: Dict containing updated member attributes
        :returns: None
        :raises MemberNotFound: The referenced member was not found
        """
        member = self._member_repo.get(db_apis.get_session(),
                                       id=member_id)

        listener = member.pool.listener
        listener.default_pool = member.pool
        load_balancer = listener.load_balancer
        vip = listener.load_balancer.vip

        update_member_tf = self._taskflow_load(self._member_flows.
                                               get_update_member_flow(),
                                               store={constants.MEMBER: member,
                                                      constants.LISTENER:
                                                      listener,
                                                      constants.LOADBALANCER:
                                                          load_balancer,
                                                      constants.VIP: vip,
                                                      constants.UPDATE_DICT:
                                                          member_updates})
        with tf_logging.DynamicLoggingListener(update_member_tf,
                                               log=LOG):
            update_member_tf.run()

    def create_pool(self, pool_id):
        """Creates a node pool.

        :param pool_id: ID of the pool to create
        :returns: None
        :raises NoSuitableLB: Unable to find the load balancer
        """
        pool = self._pool_repo.get(db_apis.get_session(),
                                   id=pool_id)

        listener = pool.listener
        listener.default_pool = pool
        load_balancer = listener.load_balancer
        vip = listener.load_balancer.vip

        create_pool_tf = self._taskflow_load(self._pool_flows.
                                             get_create_pool_flow(),
                                             store={constants.POOL: pool,
                                                    constants.LISTENER:
                                                    listener,
                                                    constants.LOADBALANCER:
                                                        load_balancer,
                                                    constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(create_pool_tf,
                                               log=LOG):
            create_pool_tf.run()

    def delete_pool(self, pool_id):
        """Deletes a node pool.

        :param pool_id: ID of the pool to delete
        :returns: None
        :raises PoolNotFound: The referenced pool was not found
        """
        pool = self._pool_repo.get(db_apis.get_session(),
                                   id=pool_id)

        load_balancer = pool.listener.load_balancer
        listener = pool.listener
        vip = load_balancer.vip

        delete_pool_tf = self._taskflow_load(
            self._pool_flows.get_delete_pool_flow(),
            store={constants.POOL: pool, constants.LISTENER: listener,
                   constants.LOADBALANCER: load_balancer,
                   constants.VIP: vip})
        with tf_logging.DynamicLoggingListener(delete_pool_tf,
                                               log=LOG):
            delete_pool_tf.run()

    def update_pool(self, pool_id, pool_updates):
        """Updates a node pool.

        :param pool_id: ID of the pool to update
        :param pool_updates: Dict containing updated pool attributes
        :returns: None
        :raises PoolNotFound: The referenced pool was not found
        """
        pool = self._pool_repo.get(db_apis.get_session(),
                                   id=pool_id)

        listener = pool.listener
        listener.default_pool = pool
        load_balancer = listener.load_balancer
        vip = listener.load_balancer.vip

        update_pool_tf = self._taskflow_load(self._pool_flows.
                                             get_update_pool_flow(),
                                             store={constants.POOL: pool,
                                                    constants.LISTENER:
                                                    listener,
                                                    constants.LOADBALANCER:
                                                        load_balancer,
                                                    constants.VIP: vip,
                                                    constants.UPDATE_DICT:
                                                        pool_updates})
        with tf_logging.DynamicLoggingListener(update_pool_tf,
                                               log=LOG):
            update_pool_tf.run()

    def failover_amphora(self, amphora_id):
        """Perform failover operations for an amphora.

        :param amphora_id: ID for amphora to failover
        :returns: None
        :raises AmphoraNotFound: The referenced amphora was not found
        """

        amp = self._amphora_repo.get(db_apis.get_session(),
                                     id=amphora_id)

        failover_amphora_tf = self._taskflow_load(
            self._amphora_flows.get_failover_flow(),
            store={constants.AMPHORA: amp,
                   constants.LOADBALANCER_ID: amp.load_balancer_id})
        with tf_logging.DynamicLoggingListener(failover_amphora_tf,
                                               log=LOG):
            failover_amphora_tf.run()

    def amphora_cert_rotation(self, amphora_id):
        """Perform cert rotation for an amphora.

        :param amphora_id: ID for amphora to rotate
        :returns: None
        :raises AmphoraNotFound: The referenced amphora was not found
        """

        amp = self._amphora_repo.get(db_apis.get_session(),
                                     id=amphora_id)
        LOG.info(_LI("Start amphora cert rotation, amphora's id is: %s")
                 % amp.id)

        certrotation_amphora_tf = self._taskflow_load(
            self._amphora_flows.cert_rotate_amphora_flow(),
            store={constants.AMPHORA: amp,
                   constants.AMPHORA_ID: amp.id})

        with tf_logging.DynamicLoggingListener(certrotation_amphora_tf,
                                               log=LOG):
            certrotation_amphora_tf.run()
