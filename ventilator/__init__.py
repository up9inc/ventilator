#!/usr/bin/ python3
# -*- coding: utf-8 -*-
from ventilator.constants import OUTPUT_DC_FILENAME
from ventilator.mock import EmptyMock, EmptyMockintoshMock, Mock
from ventilator.configurator import Configurator, ConfigFileConfigurator
from ventilator.adapter import Adapter, K8SInput, DCInput
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
        if self.mock_source:
            self.adapter = DCInput(inp, configfile_path, self.mock_source)
        else:
            self.adapter = DCInput(inp, configfile_path, None)

    def run(self):
        logging.info("We're starting")
        self._read_input()
        self._configure()
        self._read_mock_input()
        self._write_output()

    def _read_input(self):
        self.adapter.input()

    def _read_mock_input(self):
        if self.mock_source is not None:
            logging.info('Mockintosh file passed: %s', self.mock_source)
            self.adapter.mock = Mock(self.mock_source)
            self.adapter.mock.mock(type_input=self.adapter.type,
                                   mocked_input_content=self.adapter.content_configured,
                                   configfile_content=self.adapter.configurator.configuration)
        else:
            # TODO Identify Mock Source
            if self.adapter.type != 'empty' and self.adapter.valid:
                self.mock = EmptyMockintoshMock()
                self.mock.mock(self.adapter.configurator.configuration, self.adapter.file_content, self.output)

    def _configure(self):
        self.adapter.configure()

    def _write_output(self):
        file_path = self.output + '/{}'.format(OUTPUT_DC_FILENAME)
        with open(file_path, 'w') as fp:
            fp.write(self.adapter.output())
            logging.info(f"Created {self.adapter.type} file in: %s", file_path)


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
