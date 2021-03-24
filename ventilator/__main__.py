import logging

from ventilator import args
from ventilator.configurator import CLI
from ventilator import initiate

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initiate()
