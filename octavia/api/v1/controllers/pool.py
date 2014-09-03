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
import pecan
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from octavia.api.v1.controllers import base
from octavia.api.v1.controllers import health_monitor
from octavia.api.v1.controllers import member
from octavia.api.v1 import handler
from octavia.api.v1.types import pool as pool_types
from octavia.common import constants
from octavia.common import data_models
from octavia.common import exceptions
from octavia.db import api as db_api
from octavia.openstack.common import excutils


class PoolsController(base.BaseController):

    def __init__(self, load_balancer_id, listener_id):
        super(PoolsController, self).__init__()
        self.load_balancer_id = load_balancer_id
        self.listener_id = listener_id

    @wsme_pecan.wsexpose(pool_types.PoolResponse, wtypes.text)
    def get(self, id):
        session = db_api.get_session()
        db_pool = self.repositories.pool.get(session, id=id)
        if not db_pool:
            raise exceptions.NotFound(resource=data_models.Pool._name(), id=id)
        return self._convert_db_to_type(db_pool, pool_types.PoolResponse)

    @wsme_pecan.wsexpose([pool_types.PoolResponse])
    def get_all(self):
        session = db_api.get_session()
        default_pool = self.repositories.listener.get(
            session, id=self.listener_id).default_pool
        if default_pool:
            default_pool = [default_pool]
        else:
            default_pool = []
        return self._convert_db_to_type(default_pool,
                                        [pool_types.PoolResponse])

    @wsme_pecan.wsexpose(pool_types.PoolResponse, body=pool_types.PoolPOST,
                         status_code=202)
    def post(self, pool):
        session = db_api.get_session()
        if self.repositories.listener.has_pool(session, self.listener_id):
            raise exceptions.DuplicatePoolEntry()
        pool_dict = pool.to_dict()
        sp_dict = pool_dict.pop('session_persistence', None)
        pool_dict['operating_status'] = constants.OFFLINE
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        try:
            db_pool = self.repositories.create_pool_on_listener(
                session, self.listener_id, pool_dict, sp_dict=sp_dict)
        except odb_exceptions.DBError:
            # TODO(blogan): will have to do separate validation protocol
            # before creation or update since the exception messages
            # do not give any information as to what constraint failed
            raise exceptions.InvalidOption(value='', option='')
        try:
            self.handler.handle(db_pool, handler.HandlerChangeTypes.CREATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_pool = self.repositories.pool.get(session, id=db_pool.id)
        return self._convert_db_to_type(db_pool, pool_types.PoolResponse)

    @wsme_pecan.wsexpose(pool_types.PoolResponse, wtypes.text,
                         body=pool_types.PoolPUT, status_code=202)
    def put(self, id, pool):
        session = db_api.get_session()
        old_db_pool = self.repositories.pool.get(session, id=id)
        if not old_db_pool:
            raise exceptions.NotFound(resource=data_models.Pool._name(), id=id)
        pool_dict = pool.to_dict(render_unsets=False)
        pool_dict['operating_status'] = old_db_pool.operating_status
        sp_dict = pool_dict.pop('session_persistence', None)
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        try:
            self.repositories.update_pool_on_listener(session, id, pool_dict,
                                                      sp_dict)
        except odb_exceptions.DBError:
            # TODO(blogan): will have to do separate validation protocol
            # before creation or update since the exception messages
            # do not give any information as to what constraint failed
            raise exceptions.InvalidOption(value='', option='')
        db_pool = self.repositories.pool.get(session, id=id)
        try:
            self.handler.handle(db_pool, handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_pool = self.repositories.pool.get(session, id=db_pool.id)
        return self._convert_db_to_type(db_pool, pool_types.PoolResponse)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=202)
    def delete(self, id):
        session = db_api.get_session()
        db_pool = self.repositories.pool.get(session, id=id)
        if not db_pool:
            raise exceptions.NotFound(resource=data_models.Pool._name(), id=id)
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        db_pool = self.repositories.pool.get(session, id=id)
        try:
            self.handler.handle(db_pool, handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
                self.repositories.pool.update(
                    session, db_pool.id,
                    operating_status=constants.ERROR)
        db_pool = self.repositories.pool.get(session, id=db_pool.id)
        return self._convert_db_to_type(db_pool, pool_types.PoolResponse)

    @pecan.expose()
    def _lookup(self, pool_id, *remainder):
        session = db_api.get_session()
        if pool_id and len(remainder) and remainder[0] == 'members':
            remainder = remainder[1:]
            db_pool = self.repositories.pool.get(session, id=pool_id)
            if not db_pool:
                raise exceptions.NotFound(resource=data_models.Pool._name(),
                                          id=id)
            return member.MembersController(
                load_balancer_id=self.load_balancer_id,
                listener_id=self.listener_id,
                pool_id=db_pool.id), remainder
        if pool_id and len(remainder) and remainder[0] == 'healthmonitor':
            remainder = remainder[1:]
            db_pool = self.repositories.pool.get(session, id=pool_id)
            if not db_pool:
                raise exceptions.NotFound(resource=data_models.Pool._name(),
                                          id=id)
            return health_monitor.HealthMonitorController(
                load_balancer_id=self.load_balancer_id,
                listener_id=self.listener_id,
                pool_id=db_pool.id), remainder