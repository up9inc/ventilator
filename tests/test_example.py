import logging
import os
import unittest

from ventilator import Tool, ConfigFileConfigurator, K8SInput

logging.basicConfig(level=logging.DEBUG,
                    format='[%(relativeCreated)d %(name)s %(levelname)s] %(message)s')

cdir = os.path.dirname(__file__)


class K8SMockInput(K8SInput):
    def input(self):
        logging.info("K8S Mocked")

    def validate_input(self):
        pass

    def configure(self):
        pass

    def output(self):
        return "mocked"


class Tests(unittest.TestCase):
    def test_simplest(self):
        tool = Tool(cdir + "/docker-compose.yml")
        tool.run()

    def test_example(self):
        tool = Tool(cdir + "/docker-compose.yml")
        tool.configurator = ConfigFileConfigurator(cdir + "/configfile.yaml")
        tool.run()

    def test_k8s(self):
        tool = Tool("kubernetes")
        tool.adapter = K8SMockInput()
        tool.configurator = ConfigFileConfigurator(cdir + "/configfile.yaml")
        tool.run()
