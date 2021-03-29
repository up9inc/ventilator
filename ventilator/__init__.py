#!/usr/bin/ python3
# -*- coding: utf-8 -*-
from ventilator.constants import MOCKINTOSH_SERVICE, OUTPUT_DC_FILENAME
from ventilator.mock import EmptyMock, EmptyMockintoshMock
import logging
import argparse
import os
from abc import abstractmethod
from os import path
import yaml

yaml.Dumper.ignore_aliases = lambda *args: True
__version__ = "0.0.0"
__location__ = path.abspath(path.dirname(__file__))


class Tool:
    def __init__(self) -> None:
        super().__init__()
        self.output = os.getcwd()
        self.configurator = Configurator()
        self.mock = EmptyMock()
        self.configfile_path = None
        self.mock_source = None  # TODO
        self.adapter = Adapter()

    def set_k8s_configurator(self, inp=None, configfile_path=None):
        self.configfile_path = configfile_path
        self.adapter = K8SInput(inp, configfile_path)

    def set_dc_configurator(self, inp, configfile_path):
        self.configfile_path = configfile_path
        self.adapter = DCInput(inp, configfile_path)

    def run(self):
        logging.info("We're starting")
        self._read_input()
        self._configure()
        self._read_mock_input()
        self._write_output()

    def _read_input(self):
        self.adapter.input()

    def _read_mock_input(self):
        if self.mock_source:
            logging.info('Mockintosh file passed')
        else:
            # TODO Identify Mock Source
            if self.adapter.type != 'empty':
                self.mock = EmptyMockintoshMock()
                self.mock.mock(self.adapter.configurator.configuration, self.adapter.file_content, self.output)

    def _configure(self):
        self.adapter.configure()

    def _write_output(self):
        file_path = self.output + '/{}'.format(OUTPUT_DC_FILENAME)
        with open(file_path, 'w') as fp:
            fp.write(self.adapter.output())
            logging.info(f"Created {self.adapter.type} file in: %s", file_path)


class Configurator:
    configuration = None

    def configure(self):
        logging.debug("Empty configuration")


class ConfigFileConfigurator(Configurator):
    def __init__(self, conf_file=None) -> None:
        super().__init__()
        self.configuration = None
        self.conffile = conf_file

    def configure(self):
        logging.info("Reading config file: %s", self.conffile)
        with open(self.conffile) as fp:
            self.configuration = fp.read()


class Adapter:
    type = 'empty'
    configurator = Configurator()
    file_content = 'Empty Adapter'

    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def output(self):
        return self.file_content

    @abstractmethod
    def validate_input(self):
        pass

    @abstractmethod
    def configure(self):
        pass


class DCInput(Adapter):
    type = 'docker-compose'

    def __init__(self, fname, configfile_path) -> None:
        super().__init__()
        self.fname = fname
        self.file_content = None
        self.configure_services = None
        self.content_configured = {}
        self.configured_default_action = 'keep'
        self.configurator = ConfigFileConfigurator(configfile_path)
        self.configurator.configure()

    def input(self):
        logging.info("Reading the file: %s", self.fname)
        with open(self.fname, 'r') as fp:
            self.file_content = yaml.load(fp.read(), Loader=yaml.FullLoader)
        if not self.validate_input():
            logging.error("The input file: %s is not in a good format", self.fname)
            return

    def validate_input(self):
        if 'version' in self.file_content and 'services' in self.file_content:
            if self.file_content['services'] is not None and len(self.file_content['services']) > 0:
                return True
        return False

    def configure(self):
        if not self.validate_input():
            return
        self.configure_services = yaml.load(self.configurator.configuration, Loader=yaml.Loader)
        self.configured_default_action = self.configure_services['default-action'] \
            if 'default-action' in self.configure_services else self.configured_default_action
        if self.configured_default_action not in ['keep', 'mock', 'drop']:
            logging.error('Action not supported %s', self.configured_default_action)
            return
        for service_name, service_value in self.file_content['services'].items():
            if service_name in self.configure_services['services']:
                try:
                    action = self.configure_services['services'][service_name]['action']
                    print(action)
                    if action == 'mock':
                        self.mock(service_name, service_value, self.configure_services['services'][service_name])
                    elif action == 'keep':
                        self.keep(service_name, service_value)
                    elif action == 'drop':
                        pass
                    else:
                        logging.error('Action not supported %s', action)
                        return
                except TypeError:
                    logging.error('Action is required in configfile <%s>', service_name)
                    return
            else:
                self.default_action(service_name, service_value)

    def default_action(self, service_name, service_value):
        if self.configured_default_action == 'mock':
            if service_name not in self.configure_services['services']:
                self.configure_services['services'][service_name] = {"hostname": service_name, "port": '80'}
            self.mock(service_name, service_value, self.configure_services['services'][service_name])
        elif self.configured_default_action == 'keep':
            self.keep(service_name, service_value)
        elif self.configured_default_action == 'drop':
            pass

    def keep(self, service_name, service_value):
        self.content_configured[service_name] = service_value

    def mock(self, service_name, service_value, mock_service):
        self.content_configured[service_name] = {}
        if 'hostname' in mock_service:
            self.content_configured[service_name]['hostname'] = mock_service['hostname']
        elif 'hostname' in service_value:
            self.content_configured[service_name]['hostname'] = service_value['hostname']
        if 'ports' in service_value:
            self.content_configured[service_name]['ports'] = service_value['ports']
            self.content_configured[service_name]['environment'] = \
                [MOCKINTOSH_SERVICE['environment'][0].replace('80', str(service_value['ports'][0]))]
        if 'port' in mock_service:
            self.content_configured[service_name]['ports'] = [mock_service['port']]
            self.content_configured[service_name]['environment'] = \
                [MOCKINTOSH_SERVICE['environment'][0].replace('80', str(mock_service['port']))]
        self.content_configured[service_name]['command'] = MOCKINTOSH_SERVICE['command']
        self.content_configured[service_name]['image'] = MOCKINTOSH_SERVICE['image']
        self.content_configured[service_name]['cap_add'] = MOCKINTOSH_SERVICE['cap_add']
        self.content_configured[service_name]['cap_drop'] = MOCKINTOSH_SERVICE['cap_drop']
        self.content_configured[service_name]['read_only'] = MOCKINTOSH_SERVICE['read_only']
        self.content_configured[service_name]['volumes'] = MOCKINTOSH_SERVICE['volumes']

    def output(self):
        self.content_configured = {
            'version': '3',
            'services': self.content_configured
        }
        return yaml.dump(self.content_configured)


class K8SInput(Adapter):
    type = 'kubernetes'

    def validate_input(self):
        return

    def __init__(self, fname, configfile_path):
        super().__init__()
        self.fname = fname
        self.file_content = None
        self.content_configured = {}
        self.configurator = ConfigFileConfigurator(configfile_path)
        self.configurator.configure()

    def input(self):
        self.validated = self.validate_input()
        return self.validated

    def output(self):
        return 'Mock'

    def configure(self):
        return


def initiate():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configurator",
                        help="web / cli / file. Default: CLI", required=True, default="none", action='store')
    parser.add_argument("-f", "--configurator_file",
                        help="The path of the configurator file. REQUIRED if configurator is file", default="none",
                        action='store')
    parser.add_argument("-i", "--input", help="docker-compose / kubernetes file.", action='store', required=True)
    parser.add_argument("-o", "--output", help="Ventilator Output Path. Default: current directory",
                        default="", action='store')
    parser.add_argument("-mf", "--mock_source_file", help="Mock Source File", action='store', default="none")
    parser.add_argument('-v', '--verbose', help="Logging in DEBUG level", action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(asctime)s %(name)s %(levelname)s] %(message)s')
    logging.debug('DEBUG enabled')
    tool = Tool()
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
        if args.configurator_file == 'none':
            logging.error('On FILE configurator it is required -f <path_of_the_configuration_file>')
            exit(1)
        if args.mock_source_file != 'none':
            tool.mock_source = args.mock_source_file
        tool.set_dc_configurator(args.input, args.configurator_file)
    try:
        tool.run()
    except KeyboardInterrupt:
        logging.debug("Normal shutdown")
