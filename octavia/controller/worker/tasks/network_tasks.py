from oslo_config import cfg
from taskflow import task
from taskflow.types import failure


class BaseNetworkTask(task.Task):

    def __init__(self, network_driver, **kwargs):
        super(BaseNetworkTask, self).__init__(**kwargs)
        self.network = network_driver


class CreateNetworkTask(BaseNetworkTask):

    def execute(self, *args, **kwargs):
        return self.network.create_network()


class UpdateNetworkTask(BaseNetworkTask):

    def execute(self, *args, **kwargs):
        self.network.update_network()


class CreateSubnetTask(BaseNetworkTask):

    def execute(self, *args, **kwargs):
        return self.network.create_subnet()


class UpdateSubnetTask(BaseNetworkTask):

    def execute(self, *args, **kwargs):
        self.network.update_subnet()


class CreatePortTask(BaseNetworkTask):

    def execute(self, *args, **kwargs):
        return self.network.create_subnet()


class UpdatePortTask(BaseNetworkTask):

    def execute(self, *args, **kwargs):
        self.network.update_subnet()
