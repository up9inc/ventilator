import logging
import os
import unittest

from ventilator import Tool, K8SInput

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

    def test_example(self):
        tool = Tool()
        tool.set_dc_configurator(cdir + "/docker-compose.yml", cdir + '/configfile.yaml')
        tool.run()

    def test_k8s(self):
        tool = Tool()
        tool.set_k8s_configurator(None, configfile_path=cdir + "/configfile.yaml")
        tool.run()

    def test_empty_mock(self):
        tool = Tool()
        tool.mock.mock()

    def test_empty_adapter(self):
        tool = Tool()
        tool.run()
