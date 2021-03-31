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
        if services is None or len(services) == 0 or services['services'] is None:
            logging.error('Input file is empty')
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


class Mock:
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.file_content = None
        self.file_content_loaded = None
        self._identify_mock_source()

    def _identify_mock_source(self):
        try:
            with open(self.file_path, 'r') as fp:
                self.file_content = fp.read()
        except FileNotFoundError:
            logging.error('File not found: %s', self.file_path)
            exit(1)
        if len(self.file_content) <= 0:
            logging.error('Empty mock file on %s', self.file_path)
            return
        self.file_content_loaded = yaml.load(self.file_content, Loader=yaml.Loader)
        if self.file_content_loaded.get('management', False):
            if self.file_content_loaded.get('services', False):
                if len(self.file_content_loaded['services']) > 0:
                    return 'mockintosh'
                return False
            else:
                logging.error('Services not defined in Mockintosh file')
                return
        else:
            logging.error('Management field not defined in Mockintosh file')

    def mock(self, **kwargs):
        type_input = kwargs['type_input']
        if type_input == 'docker-compose':
            self._mock_dc(**kwargs)
        # TODO other cases

    def _update_command_dc(self, mocked_input_content, service_name):
        smaller_match = None
        updated = False
        for mock_service in self.file_content_loaded['services']:
            if service_name in mock_service['name']:
                if not updated:
                    smaller_match = mock_service['name']
                    updated = True
                if len(smaller_match) > len(mock_service['name']):
                    smaller_match = mock_service['name']
        if smaller_match is not None:
            mocked_input_content[service_name]['command'] = \
                f"{mocked_input_content[service_name]['command']} {smaller_match}"
        return mocked_input_content

    def _mock_dc(self, **kwargs):
        mocked_input_content = kwargs['mocked_input_content']
        configfile_content = yaml.load(kwargs['configfile_content'], Loader=yaml.Loader)
        for service_name, service_value in mocked_input_content.items():
            if service_name in configfile_content['services']:
                if 'action' in configfile_content['services'][service_name] and \
                        configfile_content['services'][service_name][
                            'action'] == 'mock':
                    mocked_input_content = self._update_command_dc(mocked_input_content, service_name)
                elif service_name not in configfile_content \
                        and configfile_content['default-action'] == 'mock':
                    if 'action' in configfile_content['services'][service_name]:
                        if configfile_content['services'][service_name]['action'] == 'mock':
                            mocked_input_content = self._update_command_dc(mocked_input_content, service_name)
                    else:
                        mocked_input_content = self._update_command_dc(mocked_input_content, service_name)
            else:
                default_action = configfile_content.get('default-action', None)
                if default_action == 'mock':
                    mocked_input_content = self._update_command_dc(mocked_input_content, service_name)
        self.mocked_content = mocked_input_content
