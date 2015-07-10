from octavia.network.drivers import neutron
from octavia.compute.drivers import nova_driver
from octavia.amphorae.drivers.haproxy import ssh_driver
from octavia.controller.worker.flows import load_balancer_flows


class DefaultFlowDriver(object):

    def __init__(self):
        # chicken and egg problem here
        self.network = neutron.NeutronDriver(None)
        self.compute = nova_driver.VirtualMachineManager(self.network)
        self.network.compute = self.compute
        self.amphora = ssh_driver.HaproxyManager(self.network, self.compute)
        self.lb_flows = load_balancer_flows.LoadBalancerFlows(
            network_driver=self.network,
            compute_driver=self.compute,
            amphora_driver=self.amphora
        )

    @property
    def create_load_balancer(self):
        return self.lb_flows.get_create_load_balancer()

    @property
    def update_load_balancer(self):
        return self.lb_flows.get_update_load_balancer_flow()

    @property
    def delete_load_balancer(self):
        return self.lb_flows.get_delete_load_balancer_flow()