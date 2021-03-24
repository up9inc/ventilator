import yaml
from ventilator.logging import logging
from ventilator.args import args
from ventilator.configurator.output import output
# from ventilator.configurator.output import 
from pprint import pprint


def CLI():
    """
        Using CLI
    """
    try:
        with open(args.input, 'r') as f:
            input_file = f.read()
    except FileNotFoundError:
        logging.error(f"File {args.input} not found")
        exit(1)

    multiple_files = False

    if '\n---\n' in input_file:
        input_file_object = yaml.load_all(input_file, Loader=yaml.Loader)
        multiple_files = True
    else: 
        input_file_object = yaml.load(input_file, Loader=yaml.Loader)    

    output(input_file_object, multiple_files)
