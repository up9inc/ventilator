#!/usr/bin/ python3
# -*- coding: utf-8 -*-

from ventilator.configurator import CLI
from ventilator.args import args
from os import path, environ
from ventilator.constants import *
from ventilator.logging import logging

__version__ = "0.0.0"
__location__ = path.abspath(path.dirname(__file__))


def initiate():
    logging.info(f"{args.configurator} Configurator")
    if args.configurator == 'CLI':
        CLI()
