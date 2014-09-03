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


class VIP(base.BaseType):
    ip_address = wtypes.wsattr(base.IPAddressType())
    net_port_id = wtypes.wsattr(wtypes.UuidType())
    subnet_id = wtypes.wsattr(wtypes.UuidType())
    floating_ip_id = wtypes.wsattr(wtypes.UuidType())
    floating_ip_network_id = wtypes.wsattr(wtypes.UuidType())


class LoadBalancerResponse(base.BaseType):
    id = wtypes.wsattr(wtypes.UuidType())
    name = wtypes.wsattr(wtypes.StringType())
    description = wtypes.wsattr(wtypes.StringType())
    provisioning_status = wtypes.wsattr(wtypes.StringType())
    operating_status = wtypes.wsattr(wtypes.StringType())
    enabled = wtypes.wsattr(bool)
    vip = wtypes.wsattr(VIP)


class LoadBalancerPOST(base.BaseType):
    name = wtypes.wsattr(wtypes.StringType(max_length=255))
    description = wtypes.wsattr(wtypes.StringType(max_length=255))
    enabled = wtypes.wsattr(bool, default=True)
    vip = wtypes.wsattr(VIP, mandatory=True)


class LoadBalancerPUT(base.BaseType):
    name = wtypes.wsattr(wtypes.StringType(max_length=255))
    description = wtypes.wsattr(wtypes.StringType(max_length=255))
    enabled = wtypes.wsattr(bool)