#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

from abc import ABCMeta, abstractmethod
from pathlib import Path


class AbstractMachine:
    __metaclass__ = ABCMeta

    """ Settings file """
    settingsFile = None

    def __init__(self, settings_file=None):
        if settings_file and Path(settings_file).is_file():
            self.settingsFile = settings_file


    @property
    @abstractmethod
    def hostname(self):
        """ Host name """

    @property
    @abstractmethod
    def os(self):
        """ OS Name """

    @property
    @abstractmethod
    def datetime(self):
        """ Date Time """

    @property
    @abstractmethod
    def ip(self):
        """ IP """

    @property
    @abstractmethod
    def platform(self):
        """ Platform """

    @property
    @abstractmethod
    def architecture(self):
        """ Architecture """

    @property
    @abstractmethod
    def version(self):
        """ Version """

    @property
    @abstractmethod
    def distrib_name(self):
        """ Distrib Name """

    @property
    @abstractmethod
    def distrib_id(self):
        """ Distrib ID """

    @property
    @abstractmethod
    def logo_path(self):
        """ Logo Path """

    @property
    @abstractmethod
    def settings_path(self):
        """ Settings Path """

    @property
    @abstractmethod
    def settings(self):
        """ Settings """

    @settings.setter
    def settings(self, value):
        """ Settings """

    @property
    @abstractmethod
    def type(self):
        """ Machine Type """
