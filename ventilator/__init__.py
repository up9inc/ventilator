#!/usr/bin/ python3
# -*- coding: utf-8 -*-
import logging
import os
from abc import abstractmethod
from os import path

from ventilator.configurator import CLI
from ventilator.constants import *

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

    def _write_output(self):
        pass


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
    def output(self):
        pass

class DCInput(Adapter):
    def __init__(self, fname) -> None:
        super().__init__()
        self.fname = fname

    def input(self):
        logging.info("Reading the file: %s", self.fname)
        pass


class K8SInput(Adapter):
    def input(self):
        raise NotImplemented()
