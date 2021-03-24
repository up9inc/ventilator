import logging
import os

from ventilator import initiate

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
                        format='[%(asctime)s %(name)s %(levelname)s] %(message)s')
    initiate()
