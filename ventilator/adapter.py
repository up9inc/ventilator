import logging
import yaml
from abc import abstractmethod

from ventilator.configurator import Configurator, ConfigFileConfigurator
from ventilator.constants import MOCKINTOSH_SERVICE
from ventilator.mock import Mock

logging = logging.getLogger(__name__)


class Adapter:
    type = 'empty'
    configurator = Configurator()
    file_content = 'Empty Adapter'

    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def output(self):
        return self.file_content

    @abstractmethod
    def validate_input(self):
        pass

    @abstractmethod
    def configure(self):
        pass


class DCInput(Adapter):
    type = 'docker-compose'

    def __init__(self, fname, configfile_path, mock_source) -> None:
        super().__init__()
        self.fname = fname
        self.file_content = None
        self.configure_services = None
        self.content_configured = {}
        self.configured_default_action = 'keep'
        self.configurator = ConfigFileConfigurator(configfile_path)
        self.configurator.configure()
        self.mock = None
        self.mock_source = None
        self.valid = True

    def input(self):
        logging.info("Reading the file: %s", self.fname)
        with open(self.fname, 'r') as fp:
            self.file_content = yaml.load(fp.read(), Loader=yaml.FullLoader)
        if not self.validate_input():
            logging.error("The input file: %s is not in a good format", self.fname)
            return

    def validate_input(self):
        if 'version' in self.file_content and 'services' in self.file_content:
            if self.file_content['services'] is not None and len(self.file_content['services']) > 0:
                return True
        return False

    def configure(self):
        if not self.validate_input():
            return
        self.configure_services = yaml.load(self.configurator.configuration, Loader=yaml.Loader)
        self.configured_default_action = self.configure_services['default-action'] \
            if 'default-action' in self.configure_services else self.configured_default_action
        if self.configured_default_action not in ['keep', 'mock', 'drop']:
            logging.error('Action not supported %s', self.configured_default_action)
            return
        for service_name, service_value in self.file_content['services'].items():
            if service_name in self.configure_services['services']:
                try:
                    action = self.configure_services['services'][service_name]['action']
                    if action == 'mock':
                        self.action_mock(service_name, service_value, self.configure_services['services'][service_name])
                    elif action == 'keep':
                        self.action_keep(service_name, service_value)
                    elif action == 'drop':
                        pass
                    else:
                        logging.error('Action not supported %s', action)
                        return
                except TypeError:
                    self.valid = False
                    logging.error('Action is required in configfile <%s>', service_name)
                    return
            else:
                self.default_action(service_name, service_value)

    def default_action(self, service_name, service_value):
        if self.configured_default_action == 'mock':
            if service_name not in self.configure_services['services']:
                self.configure_services['services'][service_name] = {"hostname": service_name, "port": '80'}
            self.action_mock(service_name, service_value, self.configure_services['services'][service_name])
        elif self.configured_default_action == 'keep':
            self.action_keep(service_name, service_value)
        elif self.configured_default_action == 'drop':
            pass

    def action_keep(self, service_name, service_value):
        self.content_configured[service_name] = service_value

    def action_mock(self, service_name, service_value, mock_service):
        self.content_configured[service_name] = {}
        if 'hostname' in mock_service:
            self.content_configured[service_name]['hostname'] = mock_service['hostname']
        elif 'hostname' in service_value:
            self.content_configured[service_name]['hostname'] = service_value['hostname']
        if 'ports' in service_value:
            self.content_configured[service_name]['ports'] = service_value['ports']
            self.content_configured[service_name]['environment'] = \
                [MOCKINTOSH_SERVICE['environment'][0].replace('80', str(service_value['ports'][0]))]
        if 'port' in mock_service:
            self.content_configured[service_name]['ports'] = [mock_service['port']]
            self.content_configured[service_name]['environment'] = \
                [MOCKINTOSH_SERVICE['environment'][0].replace('80', str(mock_service['port']))]
        self.content_configured[service_name]['command'] = MOCKINTOSH_SERVICE['command']
        self.content_configured[service_name]['image'] = MOCKINTOSH_SERVICE['image']
        self.content_configured[service_name]['cap_add'] = MOCKINTOSH_SERVICE['cap_add']
        self.content_configured[service_name]['cap_drop'] = MOCKINTOSH_SERVICE['cap_drop']
        self.content_configured[service_name]['read_only'] = MOCKINTOSH_SERVICE['read_only']
        self.content_configured[service_name]['volumes'] = MOCKINTOSH_SERVICE['volumes']

    def output(self):
        content_configured = {
            'version': '3'
        }
        if self.mock is None:
            content_configured['services'] = self.content_configured
            self.content_configured = content_configured
            return yaml.dump(self.content_configured)
        else:
            self.content_configured = content_configured
            content_configured['services'] = self.mock.mocked_content

            return yaml.dump(content_configured)


class K8SInput(Adapter):
    type = 'kubernetes'

    def validate_input(self):
        return

    def __init__(self, fname, configfile_path):
        super().__init__()
        self.fname = fname
        self.file_content = None
        self.content_configured = {}
        self.configurator = ConfigFileConfigurator(configfile_path)
        self.configurator.configure()

    def input(self):
        self.validated = self.validate_input()
        return self.validated

    def output(self):
        return 'Mock'

    def configure(self):
        return
