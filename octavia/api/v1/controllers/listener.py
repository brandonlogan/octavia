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
from octavia.api.v1.controllers import pool
from octavia.api.v1 import handler
from octavia.api.v1.types import listener as listener_types
from octavia.common import constants
from octavia.common import data_models
from octavia.common import exceptions
from octavia.db import api as db_api
from octavia.openstack.common import excutils


class ListenersController(base.BaseController):

    def __init__(self, load_balancer_id):
        super(ListenersController, self).__init__()
        self.load_balancer_id = load_balancer_id

    @wsme_pecan.wsexpose(listener_types.ListenerResponse, wtypes.text)
    def get_one(self, id):
        session = db_api.get_session()
        db_listener = self.repositories.listener.get(
            session, load_balancer_id=self.load_balancer_id, id=id)
        if not db_listener:
            raise exceptions.NotFound(
                resource=data_models.Listener._name(), id=id)
        return self._convert_db_to_type(db_listener,
                                        listener_types.ListenerResponse)

    @wsme_pecan.wsexpose([listener_types.ListenerResponse])
    def get_all(self):
        session = db_api.get_session()
        db_listeners = self.repositories.listener.get_all(
            session, load_balancer_id=self.load_balancer_id)
        return self._convert_db_to_type(db_listeners,
                                        [listener_types.ListenerResponse])

    @wsme_pecan.wsexpose(listener_types.ListenerResponse,
                         body=listener_types.ListenerPOST, status_code=202)
    def post(self, listener):
        session = db_api.get_session()
        listener_dict = listener.to_dict()
        listener_dict['load_balancer_id'] = self.load_balancer_id
        listener_dict['provisioning_status'] = constants.PENDING_CREATE
        listener_dict['operating_status'] = constants.OFFLINE
        try:
            db_listener = self.repositories.listener.create(
                session, **listener_dict)
        except odb_exceptions.DBDuplicateEntry:
            raise exceptions.DuplicateListenerEntry(
                port=listener_dict.get('protocol_port'))
        except odb_exceptions.DBError:
            raise exceptions.InvalidOption(value=listener_dict.get('protocol'),
                                           option='protocol')
        # Handler will be responsible for sending to controller
        try:
            self.handler.handle(db_listener, handler.HandlerChangeTypes.CREATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, db_listener.id,
                    provisioning_status=constants.ERROR)
        db_listener = self.repositories.listener.get(
            session, id=db_listener.id)
        return self._convert_db_to_type(db_listener,
                                        listener_types.ListenerResponse)

    @wsme_pecan.wsexpose(listener_types.ListenerResponse, wtypes.text,
                         body=listener_types.ListenerPUT, status_code=202)
    def put(self, id, listener):
        session = db_api.get_session()
        old_db_listener = self.repositories.listener.get(session, id=id)
        if not old_db_listener:
            raise exceptions.NotFound(
                resource=data_models.Listener._name(), id=id)
        listener_dict = listener.to_dict(render_unsets=False)
        listener_dict['provisioning_status'] = constants.PENDING_UPDATE
        listener_dict['operating_status'] = old_db_listener.operating_status
        try:
            self.repositories.listener.update(session, id, **listener_dict)
        except odb_exceptions.DBDuplicateEntry:
            raise exceptions.DuplicateListenerEntry(
                port=listener_dict.get('protocol_port'))
        except odb_exceptions.DBError:
            raise exceptions.InvalidOption(value=listener_dict.get('protocol'),
                                           option='protocol')
        db_listener = self.repositories.listener.get(session, id=id)
        try:
            self.handler.handle(db_listener,
                                handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, db_listener.id,
                    provisioning_status=constants.ERROR)
        db_lb = self.repositories.listener.get(session, id=db_listener.id)
        return self._convert_db_to_type(db_lb, listener_types.ListenerResponse)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=202)
    def delete(self, id):
        session = db_api.get_session()
        db_listener = self.repositories.listener.get(session, id=id)
        if not db_listener:
            raise exceptions.NotFound(
                resource=data_models.Listener._name(), id=id)
        self.repositories.listener.update(
            session, id, provisioning_status=constants.PENDING_DELETE)
        db_listener = self.repositories.listener.get(session, id=id)
        try:
            self.handler.handle(db_listener, handler.HandlerChangeTypes.DELETE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, db_listener.id,
                    provisioning_status=constants.ERROR)
        db_listener = self.repositories.listener.get(
            session, id=db_listener.id)
        return self._convert_db_to_type(db_listener,
                                        listener_types.ListenerResponse)

    @pecan.expose()
    def _lookup(self, listener_id, *remainder):
        session = db_api.get_session()
        if listener_id and len(remainder) and remainder[0] == 'pools':
            remainder = remainder[1:]
            db_listener = self.repositories.listener.get(
                session, id=listener_id)
            if not db_listener:
                raise exceptions.NotFound(
                    resource=data_models.Listener._name(), id=id)
            return pool.PoolsController(load_balancer_id=self.load_balancer_id,
                                        listener_id=db_listener.id), remainder