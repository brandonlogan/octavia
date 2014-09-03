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

import mock
import pecan
import pecan.testing

from octavia.api import config as pconfig
from octavia.tests.functional.db import base as base_db_test


class BaseAPITest(base_db_test.OctaviaDBTestBase):

    BASE_PATH = '/v1'
    LBS_PATH = '/loadbalancers'
    LB_PATH = LBS_PATH + '/{lb_id}'
    LISTENERS_PATH = LB_PATH + '/listeners'
    LISTENER_PATH = LISTENERS_PATH + '/{listener_id}'
    POOLS_PATH = LISTENER_PATH + '/pools'
    POOL_PATH = POOLS_PATH + '/{pool_id}'
    MEMBERS_PATH = POOL_PATH + '/members'
    MEMBER_PATH = MEMBERS_PATH + '/{member_id}'
    HM_PATH = POOL_PATH + '/healthmonitor'

    def setUp(self):
        super(BaseAPITest, self).setUp()
        self.app = self._make_app()
        self.mock_get_session = mock.patch('octavia.db.api.get_session')
        self.mock_session = self.mock_get_session.start()
        self.mock_session.return_value = self.session

        def reset_pecan(mock_get_session):
            pecan.set_config({}, overwrite=True)
            mock_get_session.stop()

        self.addCleanup(reset_pecan, self.mock_get_session)

    def _make_app(self):
        return pecan.testing.load_test_app({'app': pconfig.app,
                                            'wsme': pconfig.wsme})

    def _get_full_path(self, path):
        return ''.join([self.BASE_PATH, path])

    def delete(self, path, headers=None, status=202, expect_errors=False):
        headers = headers or {}
        full_path = self._get_full_path(path)
        response = self.app.delete(full_path,
                                   headers=headers,
                                   status=status,
                                   expect_errors=expect_errors)
        return response

    def post(self, path, body, headers=None, status=202, expect_errors=False):
        headers = headers or {}
        full_path = self._get_full_path(path)
        response = self.app.post_json(full_path,
                                      params=body,
                                      headers=headers,
                                      status=status,
                                      expect_errors=expect_errors)
        return response

    def put(self, path, body, headers=None, status=202, expect_errors=False):
        headers = headers or {}
        full_path = self._get_full_path(path)
        response = self.app.put_json(full_path,
                                     params=body,
                                     headers=headers,
                                     status=status,
                                     expect_errors=expect_errors)
        return response

    def get(self, path, params=None, headers=None, status=200,
            expect_errors=False):
        full_path = self._get_full_path(path)
        response = self.app.get(full_path,
                                params=params,
                                headers=headers,
                                status=status,
                                expect_errors=expect_errors)
        return response

    def create_load_balancer(self, vip, **optionals):
        req_dict = {'vip': vip}
        req_dict.update(optionals)
        response = self.post(self.LBS_PATH, req_dict)
        return response.json

    def create_listener(self, lb_id, protocol, protocol_port, **optionals):
        req_dict = {'protocol': protocol, 'protocol_port': protocol_port}
        req_dict.update(optionals)
        path = self.LISTENERS_PATH.format(lb_id=lb_id)
        response = self.post(path, req_dict)
        return response.json

    def create_pool(self, lb_id, listener_id, protocol, lb_algorithm,
                    **optionals):
        req_dict = {'protocol': protocol, 'lb_algorithm': lb_algorithm}
        req_dict.update(optionals)
        path = self.POOLS_PATH.format(lb_id=lb_id, listener_id=listener_id)
        response = self.post(path, req_dict)
        return response.json

    def create_member(self, lb_id, listener_id, pool_id, ip_address,
                      protocol_port, **optionals):
        req_dict = {'ip_address': ip_address, 'protocol_port': protocol_port}
        req_dict.update(optionals)
        path = self.MEMBERS_PATH.format(lb_id=lb_id, listener_id=listener_id,
                                        pool_id=pool_id)
        response = self.post(path, req_dict)
        return response.json

    def create_health_monitor(self, lb_id, listener_id, pool_id, type,
                              delay, timeout, fall_threshold, rise_threshold,
                              **optionals):
        req_dict = {'type': type,
                    'delay': delay,
                    'timeout': timeout,
                    'fall_threshold': fall_threshold,
                    'rise_threshold': rise_threshold}
        req_dict.update(optionals)
        path = self.HM_PATH.format(lb_id=lb_id, listener_id=listener_id,
                                   pool_id=pool_id)
        response = self.post(path, req_dict)
        return response.json