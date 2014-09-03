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

from octavia.common import data_models
from octavia.openstack.common import gettextutils as u
from octavia.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class InvalidHandlerInputObject(Exception):
    message = "Invalid Input Object %(obj_type)"

    def __init__(self, **kwargs):
        message = self.message % kwargs
        super(InvalidHandlerInputObject, self).__init__(message=message)


class HandlerChangeTypes(object):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


class NoopLoggingLoadBalancerHandler(object):
    def _create_load_balancer(self, load_balancer):
        LOG.info(u._LI("%(entity)s handling the creation of "
                       "load balancer %(id)s") %
                 {"entity": self.__class__.__name__, "id": load_balancer.id})

    def _update_load_balancer(self, load_balancer):
        LOG.info(u._LI("%(entity)s handling the update of "
                       "load balancer %(id)s") %
                 {"entity": self.__class__.__name__, "id": load_balancer.id})

    def _delete_load_balancer(self, load_balancer):
        LOG.info(u._LI("%(entity)s handling the deletion of "
                       "load balancer %(id)s") %
                 {"entity": self.__class__.__name__, "id": load_balancer.id})

    def _handle_change_type(self, obj, change_type):
        if change_type == HandlerChangeTypes.CREATE:
            self._create_load_balancer(obj)
        if change_type == HandlerChangeTypes.UPDATE:
            self._update_load_balancer(obj)
        if change_type == HandlerChangeTypes.DELETE:
            self._delete_load_balancer(obj)

    def handle(self, obj, change_type):
        if isinstance(obj, (data_models.HealthMonitor, data_models.Member)):
            self._handle_change_type(obj.pool.listener.load_balancer,
                                     change_type)
        elif isinstance(obj, data_models.Pool):
            self._handle_change_type(obj.listener.load_balancer, change_type)
        elif isinstance(obj, data_models.Listener):
            self._handle_change_type(obj.load_balancer, change_type)
        elif isinstance(obj, data_models.LoadBalancer):
            self._handle_change_type(obj, change_type)
        else:
            raise InvalidHandlerInputObject(obj_type=obj.__class__)