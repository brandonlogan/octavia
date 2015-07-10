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


class Interface(data_models.BaseDataModel):

    def __init__(self, id=None, amphora_id=None, network_id=None,
                 ip_address=None, port_id=None):
        self.id = id
        self.amphora_id = amphora_id
        self.network_id = network_id
        self.port_id = port_id
        self.ip_address = ip_address


class Delta(data_models.BaseDataModel):

    def __init__(self, amphora_id=None, compute_id=None,
                 add_nics=None, delete_nics=None):
        self.compute_id = compute_id
        self.amphora_id = amphora_id
        self.add_nics = add_nics
        self.delete_nics = delete_nics


class Network(data_models.BaseDataModel):

    def __init__(self, id_=None, name=None, subnets=None,
                 tenant_id=None, admin_state_up=None, mtu=None):
        self.id_ = id_
        self.name = name
        self.subnets = subnets
        self.tenant_id = tenant_id
        self.admin_state_up = admin_state_up
        self.mtu = mtu


class Subnet(data_models.BaseDataModel):

    def __init__(self, id_=None, name=None, network_id=None, tenant_id=None,
                 gateway_ip=None, cidr=None, ip_version=None):
        self.id_ = id_
        self.name = name
        self.network_id = network_id
        self.tenant_id = tenant_id
        self.gateway_ip = gateway_ip
        self.cidr = cidr
        self.ip_version = ip_version


class Port(data_models.BaseDataModel):

    def __init__(self, id_=None, name=None, device_id=None, device_owner=None,
                 mac_address=None, network_id=None, status=None,
                 tenant_id=None, admin_state_up=None, fixed_ips=None):
        self.id_ = id_
        self.name = name
        self.device_id = device_id
        self.device_owner = device_owner
        self.mac_address = mac_address
        self.network_id = network_id
        self.status = status
        self.tenant_id = tenant_id
        self.admin_state_up = admin_state_up
        self.fixed_ips = fixed_ips or []


class FixedIP(data_models.BaseDataModel):

    def __init__(self, subnet_id=None, ip_address=None):
        self.subnet_id = subnet_id
        self.ip_address = ip_address
