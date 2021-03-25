class InputType():
    DOCKER_COMPOSE = 'docker-compose'
    KUBERNETES = 'kubernetes'


OUTPUT_DC_FILENAME = 'docker-compose-virtual.yaml'
MOCKINTOSH_IMAGE_TAG = 'latest'
MOCKINTOSH_IMAGE = 'up9inc/mockintosh'
MOCKINTOSH_IMAGE_FULL_URL = '{}:{}'.format(MOCKINTOSH_IMAGE, MOCKINTOSH_IMAGE_TAG)
MOCKINTOSH_SERVICE = {
    'image': MOCKINTOSH_IMAGE_FULL_URL,
    'command': '/config/mockintosh.yml',
    'environment': [
        'MOCKINTOSH_FORCE_PORT=80'
    ],
    'ports': ['80'],
    'read_only': True,
    'volumes': [
        '.:/config'
    ],
    'cap_add': [
        'NET_BIND_SERVICE'
    ],
    'cap_drop': [
        'all'
    ]
}
