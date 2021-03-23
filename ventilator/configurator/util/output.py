import yaml
from os import path, mkdir
from ventilator.constants import InputType
from ventilator.logging import logging
from ventilator.args import args


def output(configuration):
    """
        Create the ventilator resources
    """
    output_path = args.output
    output_filename = 'ventilator.yaml'
    type_input = args.type_input

    if not path.exists(output_path):
        mkdir(output_path)
    if type_input == InputType().DOCKER_COMPOSE:
        output_filename = f"docker-compose-{output_filename}"
    elif type_input == InputType().KUBERNETES:
        output_filename = f"k8s-{output_filename}"

    output_full_path = path.join(output_path + '/' + output_filename)
    logging.info(output_full_path)

    with open(output_full_path, 'w+') as of:
        of.write(yaml.dump(configuration))
