# Copyright 2011-2014 OpenStack Foundation,author: Min Wang,German Eichberger
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class AmphoraLoadBalancerDriver(object):
    @abc.abstractmethod
    def update(self, listener, vip):
        """Update the amphora with a new configuration

        :param listener: listener object,
        need to use its protocol_port property
        :type listener: object
        :param vip: vip object, need to use its ip_address property
        :type vip: object
        :returns: return a value list (listener, vip, status flag--update)

        At this moment, we just build the basic structure for testing, will
        add more function along with the development
        """
        pass

    @abc.abstractmethod
    def stop(self, listener, vip):
        """Stop the listener on the vip

        :param listener: listener object,
        need to use its protocol_port property
        :type listener: object
        :param vip: vip object, need to use its ip_address property
        :type vip: object
        :returns: return a value list (listener, vip, status flag--suspend)

        At this moment, we just build the basic structure for testing, will
        add more function along with the development
        """
        pass

    @abc.abstractmethod
    def start(self, listener, vip):
        """Start the listener on the vip

        :param listener: listener object,
        need to use its protocol_port property
        :type listener: object
        :param vip : vip object, need to use its ip_address property
        :type vip: object
        :returns: return a value list (listener, vip, status flag--enable)

        At this moment, we just build the basic structure for testing, will
        add more function along with the development
        """
        pass

    @abc.abstractmethod
    def delete(self, listener, vip):
        """Delete the listener on the vip

        :param listener: listener object,
        need to use its protocol_port property
        :type listener: object
        :param vip: vip object, need to use its ip_address property
        :type vip: object
        :returns: return a value list (listener, vip, status flag--delete)

        At this moment, we just build the basic structure for testing, will
        add more function along with the development
        """
        pass

    @abc.abstractmethod
    def get_info(self, amphora):
        """Returns information about the amphora

        :param amphora: amphora object, need to use its id property
        :type amphora: object
        :returns: return a value list (amphora.id, status flag--'info')

        At this moment, we just build the basic structure for testing, will
        add more function along with the development, eventually, we want it
        to return information as:
        {"Rest Interface": "1.0", "Amphorae": "1.0",
        "packages":{"ha proxy":"1.5"}}
        some information might come from querying the amphora
        """
        pass

    @abc.abstractmethod
    def get_diagnostics(self, amphora):
        """Return ceilometer ready health

        :param amphora: amphora object, need to use its id property
        :type amphora: object
        :returns: return a value list (amphora.id, status flag--'ge
        t_diagnostics')

        At this moment, we just build the basic structure for testing, will
        add more function along with the development, eventually, we want it
        run some expensive self tests to determine if the amphora and the lbs
        are healthy the idea is that those tests are triggered more infrequent
        than the health gathering
        """
        pass

    @abc.abstractmethod
    def finalize_amphora(self, amphora):
        """It is called before listeners configured while amphora was built

        :param amphora: amphora object, need to use its id property
        :type amphora: object
        :returns: return a value list (amphora.id, status flag--'ge
        t_diagnostics')

        At this moment, we just build the basic structure for testing, will
        add more function along with the development, eventually, we want it
        run some expensive self tests to determine if the amphora and the lbs
        are healthy the idea is that those tests are triggered more infrequent
        than the health gathering
        """
        pass

    @abc.abstractmethod
    def allocate_vip(self, load_balancer):
        """Allocates a virtual ip.

        Reserves it for later use as the frontend connection of a load
        balancer.

        :param load_balancer: octavia.common.data_models.LoadBalancer instance
        :return: octavia.common.data_models.VIP
        :raises: AllocateVIPException, PortNotFound, NetworkNotFound
        """
        pass

    @abc.abstractmethod
    def deallocate_vip(self, vip):
        """Removes any resources that reserved this virtual ip.

        :param vip: octavia.common.data_models.VIP instance
        :return: None
        :raises: DeallocateVIPException, VIPInUseException,
                 VIPConfiigurationNotFound
        """
        pass

    @abc.abstractmethod
    def plug_vip(self, load_balancer, vip):
        """Plugs a virtual ip as the frontend connection of a load balancer.

        Sets up the routing of traffic from the vip to the load balancer
        and its amphorae.

        :param load_balancer: octavia.common.data_models.LoadBalancer instance
        :param vip: octavia.common.data_models.VIP instance
        :return: dict consisting of amphora_id as key and bind_ip as value.
                 bind_ip is the ip that the amphora should listen on to
                 receive traffic to load balance.
        :raises: PlugVIPException
        """
        pass

    @abc.abstractmethod
    def unplug_vip(self, load_balancer, vip):
        """Unplugs a virtual ip as the frontend connection of a load balancer.

        Removes the routing of traffic from the vip to the load balancer
        and its amphorae.

        :param load_balancer: octavia.common.data_models.LoadBalancer instance
        :param vip: octavia.common.data_models.VIP instance
        :return: octavia.common.data_models.VIP instance
        :raises: UnplugVIPException, PluggedVIPNotFound
        """
        pass

    @abc.abstractmethod
    def plug_network(self, amphora, network_id, ip_address=None):
        """Connects an existing amphora to an existing network.

        :param amphora: amphora to plug network
        :param network_id: id of a network
        :param ip_address: ip address to attempt to be assigned to interface
        :return: octavia.network.data_models.Interface instance
        :raises: PlugNetworkException, AmphoraNotFound, NetworkNotFound
        """

    @abc.abstractmethod
    def unplug_network(self, amphora, network_id, ip_address=None):
        """Disconnects an existing amphora from an existing network.

        If ip_address is not specificed, all the interfaces plugged on
        network_id should be unplugged.

        :param amphora: amphora to unplug network
        :param network_id: id of a network
        :param ip_address: specific ip_address to unplug
        :return: None
        :raises: UnplugNetworkException, AmphoraNotFound, NetworkNotFound
        """
        pass

    def update_vip(self, load_balancer):
        """Hook for the driver to update the VIP information.

        This method will be called upon the change of a load_balancer
        configuration. It is an optional method to be implemented by drivers.
        It allows the driver to update any VIP information based on the
        state of the passed in load_balancer.

        :param load_balancer: octavia.common.data_models.LoadBalancer instance
        :return: None
        """
        pass
