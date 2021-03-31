import unittest
from collections import namedtuple

from tests.util import fake_output, assert_files_equal, dc_dir, exp_dir
from ventilator import get_tool_from_args

FakeArgs = namedtuple("FakeCLIArgs", ["output", "configurator", "input"])


class Tests(unittest.TestCase):
    def test_no_args(self):
        args = FakeArgs(fake_output(), "none", None)
        with self.assertRaises(BaseException):
            get_tool_from_args(args)

    def test_dc_confnone(self):
        args = FakeArgs(fake_output(), "none", dc_dir + "/docker-compose.yml")
        tool = get_tool_from_args(args)
        tool.run()
        assert_files_equal(exp_dir + "/dc_confnone.yaml",
                           args.output + "/docker-compose-virtual.yaml")
