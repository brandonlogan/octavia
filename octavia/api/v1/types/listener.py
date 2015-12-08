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

from wsme import types as wtypes

from octavia.api.v1.types import base
from octavia.api.v1.types import pool


class TLSTermination(base.BaseType):
    certificate = wtypes.wsattr(wtypes.StringType())
    intermediate_certificate = wtypes.wsattr(wtypes.StringType())
    private_key = wtypes.wsattr(wtypes.StringType())
    passphrase = wtypes.wsattr(wtypes.StringType())


class ListenerResponse(base.BaseType):
    """Defines which attributes are to be shown on any response."""
    id = wtypes.wsattr(wtypes.UuidType())
    name = wtypes.wsattr(wtypes.StringType())
    description = wtypes.wsattr(wtypes.StringType())
    provisioning_status = wtypes.wsattr(wtypes.StringType())
    operating_status = wtypes.wsattr(wtypes.StringType())
    enabled = wtypes.wsattr(bool)
    protocol = wtypes.wsattr(wtypes.text)
    protocol_port = wtypes.wsattr(wtypes.IntegerType())
    connection_limit = wtypes.wsattr(wtypes.IntegerType())
    tls_certificate_id = wtypes.wsattr(wtypes.StringType(max_length=255))
    sni_containers = [wtypes.StringType(max_length=255)]
    project_id = wtypes.wsattr(wtypes.UuidType())
    default_pool = wtypes.wsattr(pool.PoolResponse)

    @classmethod
    def from_data_model(cls, data_model, children=False):
        listener = super(ListenerResponse, cls).from_data_model(
            data_model, children=children)
        # NOTE(blogan): we should show sni_containers for every call to show
        # a listener
        listener.sni_containers = [sni_c.tls_container_id
                                   for sni_c in data_model.sni_containers]
        if not children:
            # NOTE(blogan): do not show default_pool if the request does not
            # want to see children
            del listener.default_pool
            return listener
        if data_model.default_pool:
            listener.default_pool = pool.PoolResponse.from_data_model(
                data_model.default_pool, children=children)
        return listener


class ListenerPOST(base.BaseType):
    """Defines mandatory and optional attributes of a POST request."""
    id = wtypes.wsattr(wtypes.UuidType())
    name = wtypes.wsattr(wtypes.StringType(max_length=255))
    description = wtypes.wsattr(wtypes.StringType(max_length=255))
    enabled = wtypes.wsattr(bool, default=True)
    protocol = wtypes.wsattr(wtypes.StringType(), mandatory=True)
    protocol_port = wtypes.wsattr(wtypes.IntegerType(), mandatory=True)
    connection_limit = wtypes.wsattr(wtypes.IntegerType())
    tls_certificate_id = wtypes.wsattr(wtypes.StringType(max_length=255))
    tls_termination = wtypes.wsattr(TLSTermination)
    sni_containers = [wtypes.StringType(max_length=255)]
    project_id = wtypes.wsattr(wtypes.UuidType())
    default_pool = wtypes.wsattr(pool.PoolPOST)


class ListenerPUT(base.BaseType):
    """Defines attributes that are acceptable of a PUT request."""
    name = wtypes.wsattr(wtypes.StringType(max_length=255))
    description = wtypes.wsattr(wtypes.StringType(max_length=255))
    enabled = wtypes.wsattr(bool)
    protocol = wtypes.wsattr(wtypes.StringType())
    protocol_port = wtypes.wsattr(wtypes.IntegerType())
    connection_limit = wtypes.wsattr(wtypes.IntegerType())
    tls_certificate_id = wtypes.wsattr(wtypes.StringType(max_length=255))
    tls_termination = wtypes.wsattr(TLSTermination)
    sni_containers = [wtypes.StringType(max_length=255)]
