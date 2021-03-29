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

    def test_empty_mock(self):
        tool = Tool()
        tool.mock.mock()

    def test_empty_adapter(self):
        tool = Tool()
        tool.run()

    def test_example(self):
        tool = Tool()
        tool.set_dc_configurator(cdir + "/docker-compose.yml", cdir + '/configfile.yaml')
        tool.run()

    def test_k8s(self):
        tool = Tool()
        tool.set_k8s_configurator(None, configfile_path=cdir + "/configfile.yaml")
        tool.mock_source = 'Something'
        tool.run()

    def test_configfile_default_action(self):
        tool_keep = Tool()
        tool_keep.set_dc_configurator(cdir + "/docker-compose.yml",
                                      configfile_path=cdir + "/configfile-default-action-keep.yaml")
        tool_keep.run()
        tool_mock = Tool()
        tool_mock.set_dc_configurator(cdir + "/docker-compose.yml",
                                      configfile_path=cdir + "/configfile-default-action-mock.yaml")
        tool_mock.run()
        tool_drop = Tool()
        tool_drop.set_dc_configurator(cdir + "/docker-compose.yml",
                                      configfile_path=cdir + "/configfile-default-action-drop.yaml")
        tool_drop.run()

    def test_configfile_default_action_not_supported(self):
        tool = Tool()
        tool.set_dc_configurator(cdir + "/docker-compose.yml",
                                 configfile_path=cdir + "/configfile-default-action-not-supported.yaml")
        tool.run()

    def test_configfile_action_not_supported(self):
        tool = Tool()
        tool.set_dc_configurator(cdir + "/docker-compose.yml",
                                 configfile_path=cdir + "/configfile-action-not-supported.yaml")
        tool.run()

    def test_empty_input_file(self):
        tool = Tool()
        tool.set_dc_configurator(cdir + "/empty-input-file.yaml",
                                 configfile_path=cdir + "/configfile-action-not-supported.yaml")
        tool.run()
