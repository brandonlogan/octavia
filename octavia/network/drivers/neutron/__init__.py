from neutronclient.common import exceptions as neutron_client_exceptions
from neutronclient.neutron import client as neutron_client
from oslo_log import log as logging

from octavia.common import keystone
from octavia.network import data_models as net_data_models

LOG = logging.getLogger(__name__)
NEUTRON_VERSION = '2.0'


class NeutronDriver(object):

    def __init__(self):
        self.client = neutron_client.Client(
            NEUTRON_VERSION, session=keystone.get_session())

    def list_networks(self):
        filters = {}
        networks = self.client.list_networks(**filters)
        networks = networks.get('networks', networks)
        return [self._network_dict_to_network_dm(network)
                for network in networks]

    def get_network(self, network_id):
        return self._network_dict_to_network_dm(
            self.client.show_network(network_id))

    def create_network(self):
        pass

    def update_network(self, network_id):
        pass

    def delete_network(self, network_id):
        pass

    def list_subnets(self):
        filters = {}
        subnets = self.client.list_subnets(**filters)
        subnets = subnets.get('subnets', subnets)
        return [self._subnet_dict_to_subnet_dm(subnet) for subnet in subnets]

    def get_subnet(self, subnet_id):
        return self._subnet_dict_to_subnet_dm(
            self.client.show_subnet(subnet_id))

    def create_subnet(self):
        pass

    def update_subnet(self, subnet_id):
        pass

    def delete_subnet(self, subnet_id):
        pass

    def list_ports(self, device_id=None, subnet_id=None):
        filters = {}
        if device_id:
            filters['device_id'] = device_id
        if subnet_id:
            filters['fixed_ips'] = 'subnet_id={0}'.format(subnet_id)
        ports = self.client.list_ports(**filters)
        ports = ports.get('ports', ports)
        return [self._port_dict_to_port_dm(port) for port in ports]

    def get_port(self, port_id):
        return self._port_dict_to_port_dm(self.client.show_port(port_id))

    def create_port(self):
        pass

    def update_port(self, port_id):
        pass

    def delete_port(self, port_id):
        pass

    def _network_dict_to_network_dm(self, network_dict):
        network_dict = network_dict.get('network', network_dict)
        return net_data_models.Network(
            id_=network_dict.get('id'),
            name=network_dict.get('name'),
            subnets=network_dict.get('subnets'),
            tenant_id=network_dict.get('tenant_id'),
            admin_state_up=network_dict.get('admin_state_up'),
            mtu=network_dict.get('mtu')
        )

    def _subnet_dict_to_subnet_dm(self, subnet_dict):
        subnet_dict = subnet_dict.get('subnet', subnet_dict)
        return net_data_models.Subnet(
            id_=subnet_dict.get('id'),
            name=subnet_dict.get('name'),
            network_id=subnet_dict.get('network_id'),
            tenant_id=subnet_dict.get('tenant_id'),
            gateway_ip=subnet_dict.get('gateway_ip'),
            cidr=subnet_dict.get('cidr'),
            ip_version=subnet_dict.get('ip_version')
        )

    def _port_dict_to_port_dm(self, port_dict):
        port_dict = port_dict.get('port', port_dict)
        fixed_ip_dms = [net_data_models.FixedIP.from_dict(fixed_ip)
                        for fixed_ip in port_dict.get('fixed_ips')]
        return net_data_models.Port(
            id_=port_dict.get('id'),
            name=port_dict.get('name'),
            device_id=port_dict.get('device_id'),
            device_owner=port_dict.get('device_owner'),
            mac_address=port_dict.get('mac_address'),
            network_id=port_dict.get('network_id'),
            status=port_dict.get('status'),
            tenant_id=port_dict.get('tenant_id'),
            admin_state_up=port_dict.get('admin_state_up'),
            fixed_ips=fixed_ip_dms
        )
