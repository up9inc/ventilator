import yaml
from ventilator.logging import logging
from ventilator.args import args
from ventilator.configurator.util import output
from pprint import pprint


def CLI():
    try:
        with open(args.input, 'r') as f:
            docker_compose_file = f.read()
    except FileNotFoundError:
        logging.error(f"File {args.input} not found")
        exit(1)

    docker_compose_object = yaml.load(docker_compose_file, Loader=yaml.Loader)

    output(docker_compose_object)
