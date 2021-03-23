import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--configurator",
                    help="Web / CLI / File", default="CLI", action='store')
parser.add_argument("-t", "--type_input", help="docker-compose / kubernetes",
                    default="docker-compose", action='store')
parser.add_argument("-i", "--input", help="docker-compose file",
                    default="docker-compose.yml", action='store')
parser.add_argument("-o", "--output", help="Ventilator Output Path",
                    default="./output", action='store')

args = parser.parse_args()
