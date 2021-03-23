import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--configurator",
                    help="Web / CLI / File. Default: CLI", default="CLI", action='store')
parser.add_argument("-t", "--type_input", help="docker-compose / kubernetes. Default: docker-compose",
                    default="docker-compose", action='store')
parser.add_argument("-i", "--input", help="docker-compose / kubernetes file. Default: docker-compose.yml",
                    default="docker-compose.yml", action='store')
parser.add_argument("-o", "--output", help="Ventilator Output Path. Default: ./output",
                    default="./output", action='store')

args = parser.parse_args()
