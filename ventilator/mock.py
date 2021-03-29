import logging
import yaml
from os import path

yaml.Dumper.ignore_aliases = lambda *args: True
logging.getLogger(__name__)
__location__ = path.abspath(path.dirname(__file__))


class EmptyMock:

    def __init__(self):
        super().__init__()

    def mock(self):
        logging.info('Empty Mock')
        return None


class EmptyMockintoshMock(EmptyMock):
    def __init__(self):
        super().__init__()
        self.default_action = 'keep'
        self.configfile_content_loaded = None
        self.mockintosh_data = {'services': None}
        logging.info("Using empty mockintosh mock")

    def mock(self, configfile_content, services, output):
        print(services)
        if services is None or len(services) == 0 or services['services'] is None:
            logging.error('Input file empty')
            return False

        self.configfile_content_loaded = yaml.load(configfile_content, Loader=yaml.Loader)
        self.default_action = self.configfile_content_loaded.get('default-action',
                                                                 self.default_action)
        self.mockintosh_data['services'] = []
        current_port = 8000
        if self.default_action == 'mock':
            for service_name, service_value in services['services'].items():
                if service_name in self.configfile_content_loaded['services']:
                    if self.configfile_content_loaded['services'][service_name] is not None:
                        configfile_service_action = self.configfile_content_loaded['services'][service_name][
                            'action']
                        if configfile_service_action != 'keep' and configfile_service_action != 'drop':
                            self._mock_service(service_name, current_port)
                            current_port += 1
                else:
                    self._mock_service(service_name, current_port)
                    current_port += 1
        else:
            for service_name, service_value in services['services'].items():
                if service_name in self.configfile_content_loaded['services'] \
                        and self.configfile_content_loaded['services'][service_name]['action'] == 'mock':
                    self._mock_service(service_name, current_port)
                    current_port += 1
        with open(output + '/mockintosh.yml', 'w') as fp:
            yaml.dump(self.mockintosh_data, fp)
            logging.info("Created mockintosh config file in: %s/%s", output, 'mockintosh.yml')
        return None

    def _mock_service(self, service_name, current_port):
        self.mockintosh_data['services'].append({
            'name': service_name,
            'port': current_port
        })
        return None
