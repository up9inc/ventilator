from os import path, mkdir

import yaml

from ventilator.configurator.check_input_type import check_input


def output(configuration, multiple_files):
    """
        Create the ventilator resources
    """
    output_path = args.output
    output_filename = 'ventilator.yaml'
    check_input()
    if not path.exists(output_path):
        mkdir(output_path)

    output_full_path = path.join(output_path + '/' + output_filename)
    logging.info(output_full_path)

    with open(output_full_path, 'w+') as of:
        if multiple_files:
            of.write(yaml.dump_all(configuration))
        else:
            of.write(yaml.dump(configuration))
