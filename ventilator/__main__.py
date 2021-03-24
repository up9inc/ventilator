import argparse
import logging
import os

from ventilator import Tool, ConfigFileConfigurator

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configurator",
                        help="Web / CLI / File. Default: CLI", default="none", action='store')
    parser.add_argument("-i", "--input", help="docker-compose / kubernetes file.", action='store')
    parser.add_argument("-o", "--output", help="Ventilator Output Path. Default: current directory",
                        default="", action='store')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
                        format='[%(asctime)s %(name)s %(levelname)s] %(message)s')

    tool = Tool(args.input)
    tool.output = args.output if args.output else os.getcwd()
    if args.configurator.lower() == 'cli':
        tool.configurator = CLIConfigurator()
    elif args.configurator.lower() == 'web':
        tool.configurator = WebConfigurator()
    elif args.configurator.lower() == 'none':
        pass  # do nothing
    else:
        tool.configurator = ConfigFileConfigurator(args.configurator)

    try:
        tool.run()
    except KeyboardInterrupt:
        logging.debug("Normal shutdown")
