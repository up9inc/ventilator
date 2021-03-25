#!/usr/bin/ python3
# -*- coding: utf-8 -*-
from ventilator.configurator import CLI
from ventilator.constants import MOCKINTOSH_SERVICE, OUTPUT_DC_FILENAME, CONFIGFILE
import logging
import argparse
import os
from abc import abstractmethod
from os import path
import yaml

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
        self.adapter.configure()

    def _write_output(self):
        file_path = self.output + '/{}'.format(OUTPUT_DC_FILENAME)
        with open(file_path, 'w') as fp:
            fp.write(self.adapter.output())
            logging.info("Created file in: %s", file_path)


class Configurator:
    def configure(self):
        logging.debug("Empty configuration")


class ConfigFileConfigurator(Configurator):
    def __init__(self, conf_file=None) -> None:
        super().__init__()
        if conf_file:
            self.conffile = conf_file
        else:
            self.conffile = CONFIGFILE

    def configure(self):
        logging.info("Reading config file: %s", self.conffile)
        with open(self.conffile) as fp:
            self.configuration = fp.read()


class Adapter:
    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def output(self):
        pass

    @abstractmethod
    def validate_input(self):
        pass

    @abstractmethod
    def configure(self):
        pass


class DCInput(Adapter):
    def __init__(self, fname) -> None:
        super().__init__()
        self.fname = fname
        self.file_content = None
        self.content_configured = {}
        self.configurator = ConfigFileConfigurator()
        self.configurator.configure()
        
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
        self.configure_services = yaml.load(self.configurator.configuration, Loader=yaml.Loader)
        self.configured_default_action = self.configure_services['default-action'] \
            if 'default-action' in self.configure_services else 'include-as-is'
        for service_name, service_value in self.file_content['services'].items():

            if service_name in self.configure_services['services']:
                if 'action' in self.configure_services['services'][service_name]:
                    action = self.configure_services['services'][service_name]['action']
                    if action == 'mock':
                        self.mock(service_name, self.configure_services['services'][service_name])
                    elif action == 'include-as-is':
                        self.include_as_is(service_name, service_value)
                    elif action == 'drop':
                        pass
                    else:
                        logging.error('Action not supported %s', action)
                else:
                    self.default_action(service_name, service_value)
            else:
                self.default_action(service_name, service_value)

    def default_action(self, service_name, service_value):
        if self.configured_default_action == 'mock':
            if service_name not in self.configure_services['services']:
                self.configure_services['services'][service_name] = {"hostname": service_name, "port": '80'}
            self.mock(service_name, self.configure_services['services'][service_name])
        elif self.configured_default_action == 'include-as-is':
            self.include_as_is(service_name, service_value)
        elif self.configured_default_action == 'drop':
            pass
        else:
            logging.error('Action not supported %s', action)

    def include_as_is(self, service_name, service_value):
        self.content_configured[service_name] = service_value

    def mock(self, service_name, mock_service):
        self.content_configured[service_name] = {}
        self.content_configured[service_name]['hostname'] = mock_service['hostname']
        self.content_configured[service_name]['image'] = MOCKINTOSH_SERVICE['image']
        self.content_configured[service_name]['command'] = \
            f"{MOCKINTOSH_SERVICE['command']} http://{mock_service['hostname']}:{str(mock_service['port'])}"
        self.content_configured[service_name]['ports'] = [mock_service['port']]
        self.content_configured[service_name]['environment'] = \
            [MOCKINTOSH_SERVICE['environment'][0].replace('80', str(mock_service['port']))]
        self.content_configured[service_name]['cap_add'] = MOCKINTOSH_SERVICE['cap_add']
        self.content_configured[service_name]['cap_drop'] = MOCKINTOSH_SERVICE['cap_drop']
        self.content_configured[service_name]['read_only'] = MOCKINTOSH_SERVICE['read_only']
        self.content_configured[service_name]['volumes'] = MOCKINTOSH_SERVICE['volumes']

    def output(self):
        self.content_configured = {
            'version': '3',
            'services':  self.content_configured
        }

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
    parser.add_argument('-v', '--verbose', help="Logging in DEBUG level", action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(asctime)s %(name)s %(levelname)s] %(message)s')
    logging.debug('DEBUG enabled')
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
