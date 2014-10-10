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

import pecan
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from octavia.api.v1.controllers import base
from octavia.api.v1.controllers import listener
from octavia.api.v1 import handler
from octavia.api.v1.types import load_balancer as lb_types
from octavia.common import constants
from octavia.common import data_models
from octavia.common import exceptions
from octavia.db import api as db_api
from octavia.openstack.common import excutils
from octavia.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class LoadBalancersController(base.BaseController):

    @wsme_pecan.wsexpose(lb_types.LoadBalancerResponse, wtypes.text)
    def get_one(self, id):
        session = db_api.get_session()
        load_balancer = self.repositories.load_balancer.get(
            session, id=id)
        if not load_balancer:
            raise exceptions.NotFound(
                resource=data_models.LoadBalancer._name(), id=id)
        return self._convert_db_to_type(load_balancer,
                                        lb_types.LoadBalancerResponse)

    @wsme_pecan.wsexpose([lb_types.LoadBalancerResponse], wtypes.text)
    def get_all(self, tenant_id=None):
        # tenant_id is an optional query parameter
        session = db_api.get_session()
        load_balancers = self.repositories.load_balancer.get_all(
            session, tenant_id=tenant_id)
        return self._convert_db_to_type(load_balancers,
                                        [lb_types.LoadBalancerResponse])

    @wsme_pecan.wsexpose(lb_types.LoadBalancerResponse,
                         body=lb_types.LoadBalancerPOST, status_code=202)
    def post(self, load_balancer):
        session = db_api.get_session()
        lb_dict = load_balancer.to_dict()
        vip_dict = lb_dict.pop('vip')
        lb_dict['provisioning_status'] = constants.PENDING_CREATE
        lb_dict['operating_status'] = constants.OFFLINE
        db_lb = self.repositories.create_load_balancer_and_vip(
            session, lb_dict, vip_dict)
        # Handler will be responsible for sending to controller
        try:
            self.handler.handle(db_lb, handler.HandlerChangeTypes.CREATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.load_balancer.update(
                    session, db_lb.id, provisioning_status=constants.ERROR)
        return self._convert_db_to_type(db_lb, lb_types.LoadBalancerResponse)

    @wsme_pecan.wsexpose(lb_types.LoadBalancerResponse,
                         wtypes.text, status_code=202,
                         body=lb_types.LoadBalancerPUT)
    def put(self, id, load_balancer):
        session = db_api.get_session()
        old_db_lb = self.repositories.load_balancer.get(session, id=id)
        if not old_db_lb:
            raise exceptions.NotFound(
                resource=data_models.LoadBalancer._name(), id=id)
        try:
            self.repositories.load_balancer.test_and_set_provisioning_status(
                session, id, constants.PENDING_UPDATE)
        except exceptions.ImmutableStatus:
            raise exceptions.ImmutableObject(resource=old_db_lb._name(),
                                             id=id)
        lb_dict = load_balancer.to_dict(render_unsets=False)
        lb_dict['operating_status'] = old_db_lb.operating_status
        self.repositories.load_balancer.update(
            session, id, **lb_dict)
        db_lb = self.repositories.load_balancer.get(session, id=id)
        try:
            self.handler.handle(db_lb, handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.load_balancer.update(
                    session, db_lb.id, provisioning_status=constants.ERROR)
        return self._convert_db_to_type(db_lb, lb_types.LoadBalancerResponse)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=202)
    def delete(self, id):
        session = db_api.get_session()
        db_lb = self.repositories.load_balancer.get(session, id=id)
        if not db_lb:
            raise exceptions.NotFound(
                resource=data_models.LoadBalancer._name(), id=id)
        self.repositories.load_balancer.update(
            session, id, provisioning_status=constants.PENDING_DELETE)
        db_lb = self.repositories.load_balancer.get(session, id=id)
        try:
            self.handler.handle(db_lb, handler.HandlerChangeTypes.DELETE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.load_balancer.update(
                    session, db_lb.id, provisioning_status=constants.ERROR)
        return self._convert_db_to_type(db_lb, lb_types.LoadBalancerResponse)

    @pecan.expose()
    def _lookup(self, lb_id, *remainder):
        session = db_api.get_session()
        if lb_id and len(remainder) and remainder[0] == 'listeners':
            remainder = remainder[1:]
            db_lb = self.repositories.load_balancer.get(session, id=lb_id)
            if not db_lb:
                raise exceptions.NotFound(
                    resource=data_models.LoadBalancer._name(), id=id)
            return listener.ListenersController(
                load_balancer_id=db_lb.id), remainder