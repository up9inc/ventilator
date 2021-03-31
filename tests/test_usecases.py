import unittest
from collections import namedtuple

from tests.util import fake_output
from ventilator import get_tool_from_args

FakeArgs = namedtuple("FakeCLIArgs", ["output", "configurator"])


class Tests(unittest.TestCase):
    def test_no_args(self):
        args = FakeArgs(fake_output(), "none")
        tool = get_tool_from_args(args)
        tool.run()
        # assert_files_equal(os.path.dirname(__file__) + "/expected/noargs.yaml",
        #                   args.output + "/docker-compose-virtual.yaml")
