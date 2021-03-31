import logging

logging = logging.getLogger(__name__)


class Configurator:
    configuration = None

    def configure(self):
        logging.debug("Empty configuration")


class ConfigFileConfigurator(Configurator):
    def __init__(self, conf_file=None) -> None:
        super().__init__()
        self.configuration = None
        self.conffile = conf_file

    def configure(self):
        logging.info("Reading config file: %s", self.conffile)
        with open(self.conffile) as fp:
            self.configuration = fp.read()
