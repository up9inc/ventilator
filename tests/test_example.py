import logging
import unittest

from ventilator import Tool, ConfigFileConfigurator, K8SInput

logging.basicConfig(level=logging.DEBUG,
                    format='[%(relativeCreated)d %(name)s %(levelname)s] %(message)s')


class K8SMockInput(K8SInput):
    def input(self):
        logging.info("K8S Mocked")


class Tests(unittest.TestCase):
    def test_simplest(self):
        tool = Tool("docker-compose.yml")
        tool.run()

    def test_example(self):
        tool = Tool("docker-compose.yml")
        tool.configurator = ConfigFileConfigurator("configfile.yaml")
        tool.run()

    def test_k8s(self):
        tool = Tool("kubernetes")
        tool.adapter = K8SMockInput()
        tool.configurator = ConfigFileConfigurator("configfile.yaml")
        tool.run()
