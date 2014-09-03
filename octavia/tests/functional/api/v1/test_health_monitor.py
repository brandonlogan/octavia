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
from octavia.tests.functional.api.v1 import base


class TestHealthMonitor(base.BaseAPITest):

    def setUp(self):
        super(TestHealthMonitor, self).setUp()
        self.lb = self.create_load_balancer({})
        self.listener = self.create_listener(self.lb.get('id'),
                                             constants.PROTOCOL_HTTP, 80)
        self.pool = self.create_pool(self.lb.get('id'),
                                     self.listener.get('id'),
                                     constants.PROTOCOL_HTTP,
                                     constants.LB_ALGORITHM_ROUND_ROBIN)
        self.hm_path = self.HM_PATH.format(lb_id=self.lb.get('id'),
                                           listener_id=self.listener.get('id'),
                                           pool_id=self.pool.get('id'))

    def test_get(self):
        api_hm = self.create_health_monitor(self.lb.get('id'),
                                            self.listener.get('id'),
                                            self.pool.get('id'),
                                            constants.HEALTH_MONITOR_HTTP,
                                            1, 1, 1, 1)
        response = self.get(self.hm_path)
        response_body = response.json
        self.assertEqual(api_hm, response_body)

    def test_bad_get(self):
        self.get(self.hm_path, status=404)

    def test_create(self):
        api_hm = self.create_health_monitor(self.lb.get('id'),
                                            self.listener.get('id'),
                                            self.pool.get('id'),
                                            constants.HEALTH_MONITOR_HTTP,
                                            1, 1, 1, 1)
        self.assertEqual(constants.HEALTH_MONITOR_HTTP, api_hm.get('type'))
        self.assertEqual(1, api_hm.get('delay'))
        self.assertEqual(1, api_hm.get('timeout'))
        self.assertEqual(1, api_hm.get('fall_threshold'))
        self.assertEqual(1, api_hm.get('rise_threshold'))

    def test_bad_create(self):
        hm_json = {'name': 'test1'}
        self.post(self.hm_path, hm_json, status=400)

    def test_duplicate_create(self):
        api_hm = self.create_health_monitor(self.lb.get('id'),
                                            self.listener.get('id'),
                                            self.pool.get('id'),
                                            constants.HEALTH_MONITOR_HTTP,
                                            1, 1, 1, 1)
        self.post(self.hm_path, api_hm, status=409)

    def test_update(self):
        self.create_health_monitor(self.lb.get('id'), self.listener.get('id'),
                                   self.pool.get('id'),
                                   constants.HEALTH_MONITOR_HTTP,
                                   1, 1, 1, 1)
        new_hm = {'type': constants.HEALTH_MONITOR_HTTPS}
        self.put(self.hm_path, new_hm)
        response = self.get(self.hm_path)
        response_body = response.json
        self.assertEqual(constants.HEALTH_MONITOR_HTTPS,
                         response_body.get('type'))

    def test_bad_update(self):
        self.create_health_monitor(self.lb.get('id'), self.listener.get('id'),
                                   self.pool.get('id'),
                                   constants.HEALTH_MONITOR_HTTP,
                                   1, 1, 1, 1)
        new_hm = {'type': 'bad_type', 'delay': 2}
        self.put(self.hm_path, new_hm, status=400)

    def test_delete(self):
        api_hm = self.create_health_monitor(self.lb.get('id'),
                                            self.listener.get('id'),
                                            self.pool['id'],
                                            constants.HEALTH_MONITOR_HTTP,
                                            1, 1, 1, 1)
        response = self.get(self.hm_path)
        self.assertEqual(api_hm, response.json)
        self.delete(self.hm_path)
        response = self.get(self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=self.listener.get('id')))
        response_body = response.json
        self.assertEqual(constants.PENDING_UPDATE,
                         response_body.get('provisioning_status'))

    def test_bad_delete(self):
        self.delete(self.hm_path, status=404)