class BaseFlows(object):

    def __init__(self, network_driver=None, compute_driver=None,
                 amphora_driver=None):
        self.network_driver = network_driver
        self.compute_driver = compute_driver
        self.amphora_driver = amphora_driver