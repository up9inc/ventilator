#!/usr/bin/ python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
from abc import abstractmethod
from os import path

import yaml

from ventilator.constants import MOCKINTOSH_SERVICE, OUTPUT_DC_FILENAME

yaml.Dumper.ignore_aliases = lambda *args: True

__version__ = "0.0.0"
__location__ = path.abspath(path.dirname(__file__))
logging = logging.getLogger(__name__)


class Tool:
    def __init__(self, inp) -> None:
        super().__init__()
        if inp == 'kubernetes':
            self.adapter = K8SInput()
        else:
            self.adapter = DCInput(inp)
        self.output = os.getcwd()
        self.configurator = Configurator()
        self.mock_source = None  # TODO

    def run(self):
        logging.info("We're starting")
        self._read_input()
        self._read_mock_input()
        self._configure()
        self._write_output()

    def _read_input(self):
        self.adapter.input()

    def _read_mock_input(self):
        pass

    def _configure(self):
        self.configurator.configure()
        self.adapter.configure()

    def _write_output(self):
        fname = self.output + '/{}'.format(OUTPUT_DC_FILENAME)
        logging.info("Writing resulting config into file: %s", fname)
        with open(fname, 'w') as fp:
            fp.write(self.adapter.output())


class Configurator:
    def configure(self):
        logging.debug("Empty configuration")


class ConfigFileConfigurator(Configurator):

    def __init__(self, conf_file) -> None:
        super().__init__()
        self.conffile = conf_file

    def configure(self):
        logging.info("Reading config file: %s", self.conffile)
        with open(self.conffile) as fp:
            fp.read()


class Adapter:
    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def validate_input(self):
        pass

    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def output(self):
        return ""


class DCInput(Adapter):
    def __init__(self, fname) -> None:
        super().__init__()
        self.fname = fname
        self.file_content = None
        self.content_configured = {}

    def input(self):
        logging.info("Reading the file: %s", self.fname)
        with open(self.fname, 'r') as fp:
            self.file_content = yaml.load(fp.read(), Loader=yaml.FullLoader)
        if not self.validate_input():
            logging.error("The input file: %s is not in a good format", self.fname)
            exit(1)

    def validate_input(self):
        if 'version' in self.file_content and 'services' in self.file_content and len(
                self.file_content['services']) > 0:
            return True
        return False

    def configure(self):
        for service in self.file_content['services']:
            self.content_configured[service] = {}
            self.content_configured[service]['hostname'] = service
            self.content_configured[service]['name'] = service
            self.content_configured[service]['image'] = MOCKINTOSH_SERVICE['image']
            self.content_configured[service]['command'] = MOCKINTOSH_SERVICE['command']
            self.content_configured[service]['ports'] = MOCKINTOSH_SERVICE['ports']
            self.content_configured[service]['environment'] = MOCKINTOSH_SERVICE['environment']
            self.content_configured[service]['cap_add'] = MOCKINTOSH_SERVICE['cap_add']
            self.content_configured[service]['cap_drop'] = MOCKINTOSH_SERVICE['cap_drop']
            self.content_configured[service]['read_only'] = MOCKINTOSH_SERVICE['read_only']
            self.content_configured[service]['volumes'] = MOCKINTOSH_SERVICE['volumes']

    def output(self):
        return yaml.dump(self.content_configured)


class K8SInput(Adapter):
    def input(self):
        raise NotImplementedError()


def initiate():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configurator",
                        help="Web / CLI / File. Default: CLI", default="none", action='store')
    parser.add_argument("-i", "--input", help="docker-compose / kubernetes file.", action='store', required=True)
    parser.add_argument("-o", "--output", help="Ventilator Output Path. Default: current directory",
                        default="", action='store')

    args = parser.parse_args()

    tool = Tool(args.input)
    tool.output = args.output if args.output else os.getcwd()
    if args.configurator.lower() == 'cli':
        # tool.configurator = CLIConfigurator()
        raise NotImplementedError()
    elif args.configurator.lower() == 'web':
        # tool.configurator = WebConfigurator()
        raise NotImplementedError()
    elif args.configurator.lower() == 'none':
        pass  # do nothing
    else:
        tool.configurator = ConfigFileConfigurator(args.configurator)
    try:
        tool.run()
    except KeyboardInterrupt:
        logging.debug("Normal shutdown")
