import unittest
from collections import namedtuple

from tests.util import fake_output, assert_files_equal, dc_dir, exp_dir, conf_dir
from ventilator import get_tool_from_args

FakeArgs = namedtuple("FakeCLIArgs", ["output", "configurator", "input", "configurator_file", "mock_source_file"])


class Tests(unittest.TestCase):
    def test_no_args(self):
        args = FakeArgs(fake_output(), "none", None, None, None)
        with self.assertRaises(BaseException):
            get_tool_from_args(args)

    def test_dc_confnone(self):
        args = FakeArgs(fake_output(), "none", dc_dir + "/docker-compose.yml", None, None)
        tool = get_tool_from_args(args)
        tool.run()
        assert_files_equal(exp_dir + "/dc_confnone.yaml",
                           args.output + "/docker-compose-virtual.yaml")

    def test_dc_conffile(self):
        args = FakeArgs(fake_output(), "file", dc_dir + "/docker-compose.yml", conf_dir + "/configfile.yaml", None)
        tool = get_tool_from_args(args)
        tool.run()
        assert_files_equal(exp_dir + "/dc_confnone.yaml",
                           args.output + "/docker-compose-virtual.yaml")
