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


class TestMember(base.BaseAPITest):

    def setUp(self):
        super(TestMember, self).setUp()
        self.lb = self.create_load_balancer({})
        self.listener = self.create_listener(self.lb.get('id'),
                                             constants.PROTOCOL_HTTP, 80)
        self.pool = self.create_pool(self.lb.get('id'),
                                     self.listener.get('id'),
                                     constants.PROTOCOL_HTTP,
                                     constants.LB_ALGORITHM_ROUND_ROBIN)
        self.members_path = self.MEMBERS_PATH.format(
            lb_id=self.lb.get('id'), listener_id=self.listener.get('id'),
            pool_id=self.pool.get('id'))
        self.member_path = self.members_path + '/{member_id}'

    def test_get(self):
        api_member = self.create_member(self.lb.get('id'),
                                        self.listener.get('id'),
                                        self.pool.get('id'),
                                        '10.0.0.1', 80)
        response = self.get(self.member_path.format(
            member_id=api_member.get('id')))
        response_body = response.json
        self.assertEqual(api_member, response_body)

    def test_bad_get(self):
        self.get(self.member_path.format(member_id=uuidutils.generate_uuid()),
                 status=404)

    def test_get_all(self):
        api_m_1 = self.create_member(self.lb.get('id'),
                                     self.listener.get('id'),
                                     self.pool.get('id'),
                                     '10.0.0.1', 80)
        api_m_2 = self.create_member(self.lb.get('id'),
                                     self.listener.get('id'),
                                     self.pool.get('id'),
                                     '10.0.0.2', 80)
        response = self.get(self.members_path)
        response_body = response.json
        self.assertIsInstance(response_body, list)
        self.assertEqual(2, len(response_body))
        self.assertIn(api_m_1, response_body)
        self.assertIn(api_m_2, response_body)

    def test_empty_get_all(self):
        response = self.get(self.members_path)
        response_body = response.json
        self.assertIsInstance(response_body, list)
        self.assertEqual(0, len(response_body))

    def test_create(self):
        api_member = self.create_member(self.lb.get('id'),
                                        self.listener.get('id'),
                                        self.pool.get('id'),
                                        '10.0.0.1', 80)
        self.assertEqual('10.0.0.1', api_member.get('ip_address'))
        self.assertEqual(80, api_member.get('protocol_port'))

    def test_bad_create(self):
        api_member = {'name': 'test1'}
        self.post(self.members_path, api_member, status=400)

    def test_duplicate_create(self):
        member = {'ip_address': '10.0.0.1', 'protocol_port': 80}
        self.post(self.members_path, member, status=202)
        self.post(self.members_path, member, status=409)

    def test_update(self):
        api_member = self.create_member(self.lb.get('id'),
                                        self.listener.get('id'),
                                        self.pool.get('id'),
                                        '10.0.0.1', 80)
        new_member = {'protocol_port': 88}
        self.put(self.member_path.format(member_id=api_member.get('id')),
                 new_member, status=202)
        response = self.get(self.member_path.format(
            member_id=api_member.get('id')))
        response_body = response.json
        self.assertEqual(88, response_body.get('protocol_port'))

    def test_bad_update(self):
        # TODO(TrevorV):  Eventually remove "expect_errors" for specific error
        api_member = self.create_member(self.lb.get('id'),
                                        self.listener.get('id'),
                                        self.pool.get('id'),
                                        '10.0.0.1', 80)
        new_member = {'protocol_port': 'ten'}
        self.put(self.member_path.format(member_id=api_member.get('id')),
                 new_member, expect_errors=True)

    def test_duplicate_update(self):
        member = {'ip_address': '10.0.0.1', 'protocol_port': 80}
        self.post(self.members_path, member)
        member['protocol_port'] = 81
        response = self.post(self.members_path, member)
        member2 = response.json
        member['protocol_port'] = 80
        self.put(self.member_path.format(member_id=member2.get('id')),
                 member, status=409)

    def test_delete(self):
        api_member = self.create_member(self.lb.get('id'),
                                        self.listener.get('id'),
                                        self.pool.get('id'),
                                        '10.0.0.1', 80)
        response = self.get(self.member_path.format(
            member_id=api_member.get('id')))
        self.assertEqual(api_member, response.json)
        self.delete(self.member_path.format(member_id=api_member.get('id')))
        response = self.get(self.LISTENER_PATH.format(
            lb_id=self.lb.get('id'), listener_id=self.listener.get('id')))
        response_body = response.json
        self.assertEqual(constants.PENDING_UPDATE,
                         response_body.get('provisioning_status'))

    def test_bad_delete(self):
        self.delete(self.member_path.format(
            member_id=uuidutils.generate_uuid()), status=404)