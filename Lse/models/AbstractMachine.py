#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

from abc import ABCMeta, abstractmethod


class AbstractMachine:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

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
    def distribName(self):
        """ Distrib Name """

    @property
    @abstractmethod
    def distribId(self):
        """ Distrib ID """
