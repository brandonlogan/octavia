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
from octavia.openstack.common import uuidutils
from octavia.tests.functional.api.v1 import base


class TestListener(base.BaseAPITest):

    def setUp(self):
        super(TestListener, self).setUp()
        self.lb = self.create_load_balancer({})
        self.listeners_path = self.LISTENERS_PATH.format(
            lb_id=self.lb.get('id'))

        def delete_lb(client, path):
            client.delete(path)

        self.addCleanup(delete_lb, self, self.LB_PATH.format(
            lb_id=self.lb.get('id')))

    def test_get_all(self):
        listener1 = self.create_listener(self.lb.get('id'),
                                         constants.PROTOCOL_HTTP, 80)
        listener2 = self.create_listener(self.lb.get('id'),
                                         constants.PROTOCOL_HTTP, 81)
        listener3 = self.create_listener(self.lb.get('id'),
                                         constants.PROTOCOL_HTTP, 82)
        response = self.get(self.listeners_path)
        api_lbs = response.json
        self.assertEqual(3, len(api_lbs))
        self.assertIn(listener1, api_lbs)
        self.assertIn(listener2, api_lbs)
        self.assertIn(listener3, api_lbs)

    def test_get_all_bad_lb_id(self):
        path = self.LISTENERS_PATH.format(lb_id='SEAN-CONNERY')
        self.get(path, status=404)

    def test_get(self):
        listener = self.create_listener(self.lb.get('id'),
                                        constants.PROTOCOL_HTTP, 80)
        listener_path = self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=listener.get('id'))
        response = self.get(listener_path)
        api_lb = response.json
        expected = {'name': None, 'description': None, 'enabled': True,
                    'operating_status': constants.OFFLINE,
                    'provisioning_status': constants.PENDING_CREATE,
                    'connection_limit': None}
        listener.update(expected)
        self.assertEqual(listener, api_lb)

    def test_get_bad_listener_id(self):
        listener_path = self.LISTENER_PATH.format(lb_id=self.lb.get('id'),
                                                  listener_id='SEAN-CONNERY')
        self.get(listener_path, status=404)

    def test_create(self):
        lb_listener = {'name': 'listener1', 'description': 'desc1',
                       'enabled': False, 'protocol': constants.PROTOCOL_HTTP,
                       'protocol_port': 80, 'connection_limit': 10}
        response = self.post(self.listeners_path, lb_listener)
        listener_api = response.json
        extra_expects = {'provisioning_status': constants.PENDING_CREATE,
                         'operating_status': constants.OFFLINE}
        lb_listener.update(extra_expects)
        self.assertTrue(uuidutils.is_uuid_like(listener_api.get('id')))
        lb_listener['id'] = listener_api.get('id')
        self.assertEqual(lb_listener, listener_api)

    def test_create_defaults(self):
        defaults = {'name': None, 'description': None, 'enabled': True,
                    'connection_limit': None}
        lb_listener = {'protocol': constants.PROTOCOL_HTTP,
                       'protocol_port': 80}
        response = self.post(self.listeners_path, lb_listener)
        listener_api = response.json
        extra_expects = {'provisioning_status': constants.PENDING_CREATE,
                         'operating_status': constants.OFFLINE}
        lb_listener.update(extra_expects)
        lb_listener.update(defaults)
        self.assertTrue(uuidutils.is_uuid_like(listener_api.get('id')))
        lb_listener['id'] = listener_api.get('id')
        self.assertEqual(lb_listener, listener_api)

    def test_update(self):
        listener = self.create_listener(self.lb.get('id'),
                                        constants.PROTOCOL_TCP, 80,
                                        name='listener1', description='desc1',
                                        enabled=False, connection_limit=10)
        new_listener = {'name': 'listener2', 'enabled': True}
        listener_path = self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=listener.get('id'))
        response = self.put(listener_path, new_listener)
        api_listener = response.json
        update_expect = {'name': 'listener2', 'enabled': True,
                         'provisioning_status': constants.PENDING_UPDATE,
                         'operating_status': constants.OFFLINE}
        listener.update(update_expect)
        self.assertEqual(listener, api_listener)
        response = self.get(listener_path)
        api_listener = response.json
        self.assertEqual(listener, api_listener)

    def test_update_bad_listener_id(self):
        listener_path = self.LISTENER_PATH.format(lb_id=self.lb.get('id'),
                                                  listener_id='SEAN-CONNERY')
        self.put(listener_path, body={}, status=404)

    def test_create_listeners_same_port(self):
        listener1 = self.create_listener(self.lb.get('id'),
                                         constants.PROTOCOL_TCP, 80)
        listener2_post = {'protocol': listener1.get('protocol'),
                          'protocol_port': listener1.get('protocol_port')}
        self.post(self.listeners_path, listener2_post, status=409)

    def test_update_listeners_same_port(self):
        listener1 = self.create_listener(self.lb.get('id'),
                                         constants.PROTOCOL_TCP, 80)
        listener2 = self.create_listener(self.lb.get('id'),
                                         constants.PROTOCOL_TCP, 81)
        listener2_put = {'protocol': listener1.get('protocol'),
                         'protocol_port': listener1.get('protocol_port')}
        listener2_path = self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=listener2.get('id'))
        self.put(listener2_path, listener2_put, status=409)

    def test_delete(self):
        listener = self.create_listener(self.lb.get('id'),
                                        constants.PROTOCOL_HTTP, 80)
        listener_path = self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=listener.get('id'))
        self.delete(listener_path)
        response = self.get(listener_path)
        api_lb = response.json
        expected = {'name': None, 'description': None, 'enabled': True,
                    'operating_status': constants.OFFLINE,
                    'provisioning_status': constants.PENDING_DELETE,
                    'connection_limit': None}
        listener.update(expected)
        self.assertEqual(listener, api_lb)

    def test_delete_bad_listener_id(self):
        listener_path = self.LISTENER_PATH.format(lb_id=self.lb.get('id'),
                                                  listener_id='SEAN-CONNERY')
        self.delete(listener_path, status=404)

    def test_create_listener_bad_protocol(self):
        lb_listener = {'protocol': 'SEAN_CONNERY',
                       'protocol_port': 80}
        self.post(self.listeners_path, lb_listener, status=400)

    def test_update_listener_bad_protocol(self):
        listener = self.create_listener(self.lb.get('id'),
                                        constants.PROTOCOL_TCP, 80)
        new_listener = {'protocol': 'SEAN_CONNERY',
                        'protocol_port': 80}
        listener_path = self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=listener.get('id'))
        self.put(listener_path, new_listener, status=400)