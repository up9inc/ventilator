import logging
import os
import unittest
from tests.util import fake_output, dc_dir, conf_dir
from ventilator import Tool, K8SInput, parse_cli_args, get_tool_from_args
from ventilator.exceptions import ActionNotSupported, DockerComposeNotInAGoodFormat
from ventilator.exceptions import InvalidConfigfileDefinition, InvalidConfigfileDefinitionAction

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
        tool.adapter = None
        tool.input = dc_dir + '/docker-compose.yml'
        tool.run()

    def test_single_run(self):
        args = parse_cli_args().parse_args([
            '--input', dc_dir + '/docker-compose.yml',
            '--output', fake_output(),
            '--configurator', 'file',
            '--configurator_file', conf_dir + '/configfile.yaml',
            '--mock_source_file', conf_dir + '/../mockintosh/mockintosh.yml'
        ])
        tool = get_tool_from_args(args)
        tool.run()

    def test_dc_empty_mock_source(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/docker-compose.yml", conf_dir + '/configfile.yaml')
        tool.run()

    def test_dc_mock_source(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/docker-compose.yml", conf_dir + '/configfile.yaml')
        tool.mock_source = dc_dir + '/../mockintosh/mockintosh.yml'
        tool.run()

    def test_example_broken_configfile(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/docker-compose.yml", conf_dir + '/configfile-broken.yaml')
        self.assertRaises(InvalidConfigfileDefinition, tool.run)

    def test_example_broken_configfile_action(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/docker-compose.yml", conf_dir + '/configfile-broken-action.yaml')
        self.assertRaises(InvalidConfigfileDefinitionAction, tool.run)

    def test_k8s(self):
        tool = Tool()
        tool.set_k8s_configurator(None, configfile_path=conf_dir + "/configfile.yaml")
        tool.run()

    def test_configfile_default_action(self):
        tool_keep = Tool()
        tool_keep.set_dc_configurator(dc_dir + "/docker-compose.yml",
                                      configfile_path=conf_dir + "/configfile-default-action-keep.yaml")
        tool_keep.run()
        tool_mock = Tool()
        tool_mock.set_dc_configurator(dc_dir + "/docker-compose.yml",
                                      configfile_path=conf_dir + "/configfile-default-action-mock.yaml")
        tool_mock.run()
        tool_drop = Tool()
        tool_drop.set_dc_configurator(dc_dir + "/docker-compose.yml",
                                      configfile_path=conf_dir + "/configfile-default-action-drop.yaml")
        tool_drop.run()

    def test_configfile_default_action_not_supported(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/docker-compose.yml",
                                 configfile_path=conf_dir + "/configfile-default-action-not-supported.yaml")
        self.assertRaises(ActionNotSupported, tool.run)

    def test_configfile_action_not_supported(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/docker-compose.yml",
                                 configfile_path=conf_dir + "/configfile-action-not-supported.yaml")
        self.assertRaises(ActionNotSupported, tool.run)

    def test_empty_input_file(self):
        tool = Tool()
        tool.set_dc_configurator(dc_dir + "/empty-input-file.yaml",
                                 configfile_path=conf_dir + "/configfile-action-not-supported.yaml")
        self.assertRaises(DockerComposeNotInAGoodFormat, tool.run)
