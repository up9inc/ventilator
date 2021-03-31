import difflib
import logging
import os
import shutil
import sys
import tempfile
import time

is_debug = 'pydevd' in sys.modules and not os.getenv("CI", False) or os.environ.get('DEBUG', "")
exp_dir = os.path.dirname(__file__) + "/expected"
dc_dir = os.path.dirname(__file__) + "/docker-compose"
conf_dir = os.path.dirname(__file__) + "/configs"


def fake_output():
    base = os.path.dirname(__file__) + "/../tests-outputs"
    os.makedirs(base, exist_ok=True)
    dirname = tempfile.mkdtemp(dir=base, prefix="%s-" % time.time())
    return dirname


def assert_files_equal(expected, actual, replace_str="", replace_with="", debug_overwrite=True):
    with open(expected, 'a'):
        pass

    with open(expected) as exp, open(actual) as act:
        act_lines = [x.replace(replace_str, replace_with).rstrip() for x in act.readlines()]
        exp_lines = [x.replace(replace_str, replace_with).rstrip() for x in exp.readlines()]

    diff = list(difflib.unified_diff(exp_lines, act_lines, fromfile=expected, tofile=actual))
    if diff:
        if replace_str:
            logging.info("Replacements are: %s => %s", replace_str, replace_with)

        msg = "Failed asserting that two files are equal, diff is:\n\n%s"
        if is_debug and debug_overwrite:
            shutil.copy(actual, expected)
        raise AssertionError(msg % "\n".join(diff))
