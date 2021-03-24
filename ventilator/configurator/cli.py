import yaml

from ventilator.configurator.output import output


def CLI():
    """
        Using CLI
    """
    try:
        with open(args.adapter, 'r') as f:
            input_file = f.read()
    except FileNotFoundError:
        logging.error(f"File {args.adapter} not found")
        exit(1)

    multiple_files = False

    if '\n---\n' in input_file:
        input_file_object = yaml.load_all(input_file, Loader=yaml.Loader)
        multiple_files = True
    else: 
        input_file_object = yaml.load(input_file, Loader=yaml.Loader)    

    output(input_file_object, multiple_files)
