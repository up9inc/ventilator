#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
.. module:: __init__
    :synopsis: module that contains the exceptions.
"""


class DockerComposeNotInAGoodFormat(Exception):
    """
        Raised in case of a docker-compose file is not in an acceptable format.
    """

    def __init__(self):
        super().__init__("Docker compose input not in a good format")


class ActionNotSupported(Exception):
    """
        Raised in case of user uses an action that is not supported.
    """

    def __init__(self, cause):
        super().__init__(f"Action {cause} not supported. Maybe a typo?")


class InvalidConfigfileDefinitionAction(Exception):
    """
        Raised in case of user not pass an action attribute in a service field.
    """

    def __init__(self):
        super().__init__("Action is required in configfile")


class InvalidConfigfileDefinition(Exception):
    """
        Raised in case of user not pass an action attribute in a service field.
    """

    def __init__(self):
        super().__init__("Invalid configfile")


class InvalidMockintoshFile(Exception):
    """
      Raised in case of mockintosh file doesn't have services field, or is empty.
    """

    def __init__(self):
        super().__init__('One of following fields was not defined in Mockintosh file: services, management')
