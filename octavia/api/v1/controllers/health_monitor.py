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

from oslo.db import exception as odb_exceptions
from wsmeext import pecan as wsme_pecan

from octavia.api.v1.controllers import base
from octavia.api.v1 import handler
from octavia.api.v1.types import health_monitor as hm_types
from octavia.common import constants
from octavia.common import data_models
from octavia.common import exceptions
from octavia.db import api as db_api
from octavia.openstack.common import excutils


class HealthMonitorController(base.BaseController):

    def __init__(self, load_balancer_id, listener_id, pool_id):
        super(HealthMonitorController, self).__init__()
        self.load_balancer_id = load_balancer_id
        self.listener_id = listener_id
        self.pool_id = pool_id

    @wsme_pecan.wsexpose(hm_types.HealthMonitorResponse)
    def get_all(self):
        # NOTE(blogan): since a pool can only have one health monitor
        # we are using the get_all method to only get the single health monitor
        session = db_api.get_session()
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        if not db_hm:
            raise exceptions.NotFound(
                resource=data_models.HealthMonitor._name(), id=id)
        return self._convert_db_to_type(db_hm, hm_types.HealthMonitorResponse)

    @wsme_pecan.wsexpose(hm_types.HealthMonitorResponse,
                         body=hm_types.HealthMonitorPOST, status_code=202)
    def post(self, health_monitor):
        session = db_api.get_session()
        try:
            db_hm = self.repositories.health_monitor.get(
                session, pool_id=self.pool_id)
            if db_hm:
                raise exceptions.DuplicateHealthMonitor()
        except exceptions.NotFound:
            pass
        hm_dict = health_monitor.to_dict()
        hm_dict['pool_id'] = self.pool_id
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        try:
            db_hm = self.repositories.health_monitor.create(session, **hm_dict)
        except odb_exceptions.DBError:
            raise exceptions.InvalidOption(value=hm_dict.get('type'),
                                           option='type')
        try:
            self.handler.handle(db_hm, handler.HandlerChangeTypes.CREATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        return self._convert_db_to_type(db_hm, hm_types.HealthMonitorResponse)

    @wsme_pecan.wsexpose(hm_types.HealthMonitorResponse,
                         body=hm_types.HealthMonitorPUT, status_code=202)
    def put(self, health_monitor):
        session = db_api.get_session()
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        if not db_hm:
            raise exceptions.NotFound(
                resource=data_models.HealthMonitor._name(), id=id)
        hm_dict = health_monitor.to_dict(render_unsets=False)
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        try:
            self.repositories.health_monitor.update(
                session, self.pool_id, **hm_dict)
        except odb_exceptions.DBError:
            raise exceptions.InvalidOption(value=hm_dict.get('type'),
                                           option='type')
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        try:
            self.handler.handle(db_hm, handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        return self._convert_db_to_type(db_hm, hm_types.HealthMonitorResponse)

    @wsme_pecan.wsexpose(None, status_code=202)
    def delete(self):
        session = db_api.get_session()
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        if not db_hm:
            raise exceptions.NotFound(
                resource=data_models.HealthMonitor._name(), id=id)
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        db_hm = self.repositories.health_monitor.get(session,
                                                     pool_id=self.pool_id)
        try:
            self.handler.handle(db_hm, handler.HandlerChangeTypes.DELETE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_hm = self.repositories.health_monitor.get(
            session, pool_id=self.pool_id)
        return self._convert_db_to_type(db_hm, hm_types.HealthMonitorResponse)
