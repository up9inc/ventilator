import yaml
from os import path, mkdir, system
from ventilator.constants import InputType
from ventilator.logging import logging
from ventilator.args import args
import re


def is_docker_compose(file_content):
    if 'version:' in file_content and 'services:' in file_content:
        out = system(f"docker-compose -f {args.input} config -q --no-interpolate ")
        if out:
            logging.error('Invalid docker-compose file')
            exit(1)
        return True
    return False


def is_kubernetes_resource(file_content):
    if 'apiVersion' in file_content and 'kind' in file_content and 'metadata' in file_content:
        return True
    return False


def check_input():
    file_path = args.input
    with open(file_path, 'r') as f:
        file_content = f.read()
        if is_docker_compose(file_content):
            return InputType().DOCKER_COMPOSE
        elif is_kubernetes_resource(file_content):
            return InputType().KUBERNETES
        else:
            logging.error('File input type not supported')
            exit(1)
