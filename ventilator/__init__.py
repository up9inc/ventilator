#!/usr/bin/ python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
from os import path
from pathlib import Path

from shutil import copyfile, SameFileError

import yaml

from ventilator.adapter import EmptyAdapter, K8SInput, DCInput
from ventilator.configurator import Configurator
from ventilator.constants import OUTPUT_DC_FILENAME
from ventilator.mock import EmptyMock, EmptyMockintoshMock, Mock

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
        self.adapter = None

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
        if not hasattr(self.adapter, 'input') and not hasattr(self, 'input'):
            logging.info("Empty input, doing nothing...")
            return
        self._read_input()
        self._configure()
        self._read_mock_input()
        self._copy_dependency_files()
        self._write_output()

    def _read_input(self):
        if self.adapter is None:
            self.adapter = EmptyAdapter(self.input)
        self.adapter.input()

    def _read_mock_input(self):
        if isinstance(self.adapter, EmptyAdapter):
            return
        if self.mock_source is not None:
            logging.info('Mockintosh file passed: %s', self.mock_source)
            self.adapter.mock = Mock(self.mock_source)
            self.adapter.mock.mock(type_input=self.adapter.type,
                                   mocked_input_content=self.adapter.content_configured,
                                   configfile_content=self.adapter.configurator.configuration)
        else:
            # TODO Identify Mock Source
            if self.adapter.type != 'empty':
                self.mock = EmptyMockintoshMock()
                self.mock.mock(self.adapter.type, self.adapter.configurator.configuration, self.adapter.file_content,
                               self.output)

    def _configure(self):
        self.adapter.configure()

    def _copy_dependency_files(self):
        if isinstance(self.adapter.mock, EmptyMock) or self.adapter.mock is None:
            return
        logging.info(self.adapter.mock.file_list)
        for file_to_be_copied in self.adapter.mock.file_list:
            file_path = path.join(self.output, file_to_be_copied)
            logging.info(file_path)
            file_directory = path.join(str(Path().absolute()), '/'.join(
                file_path.split('/')[0:len(file_path.split('/')) - 1]))
            try:
                Path(file_directory).mkdir(parents=True)
            except FileExistsError:
                pass
            try:
                copyfile(file_to_be_copied, file_path)
                logging.info(f"{file_path} Created.")
            except SameFileError:
                pass

    def _write_output(self):
        file_path = self.output + '/{}'.format(OUTPUT_DC_FILENAME)
        with open(file_path, 'w') as fp:
            fp.write(self.adapter.output())
            logging.info(f"Created {self.adapter.type} file in: %s", file_path)


def parse_cli_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configurator",
                        help="web / cli / file / none. Default: none", required=False, default=None, action='store')
    parser.add_argument("-f", "--configurator_file",
                        help="The path of the configurator file. REQUIRED if configurator is file", default=None,
                        action='store')
    parser.add_argument("-i", "--input", help="docker-compose / kubernetes file.", action='store', required=True)
    parser.add_argument("-o", "--output", help="Ventilator Output Path. Default: current directory",
                        default="", action='store')
    parser.add_argument("-mf", "--mock_source_file", help="Mock Source File", action='store', default=None)
    parser.add_argument('-v', '--verbose', help="Logging in DEBUG level", action='store_true')
    return parser


def initiate():
    args = parse_cli_args().parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(asctime)s %(name)s %(levelname)s] %(message)s')
    logging.debug('DEBUG enabled')

    tool = get_tool_from_args(args)

    try:
        tool.run()
    except KeyboardInterrupt:
        logging.debug("Normal shutdown")


def get_tool_from_args(args):
    if args.input is None or len(args.input) == 0:
        raise BaseException('No default input or ')
    tool = Tool()
    tool.output = args.output if args.output else os.getcwd()
    if args.configurator is None:
        tool.input = args.input
        pass  # do nothing
    elif args.configurator.lower() == 'cli':
        # tool.configurator = CLIConfigurator()
        raise NotImplementedError()
    elif args.configurator.lower() == 'web':
        # tool.configurator = WebConfigurator()
        raise NotImplementedError()
    else:
        if args.configurator_file is None:
            raise BaseException('On FILE configurator it is required -f <path_of_the_configuration_file>')
        if args.mock_source_file != 'none':
            tool.mock_source = args.mock_source_file
        tool.set_dc_configurator(args.input, args.configurator_file)
    return tool
