#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import datetime
import platform
import socket

from Lse.models import AbstractMachine


class LocalMachine(AbstractMachine):

    def __init__(self):
        super().__init__()

    @property
    def version(self):
        return platform.version()

    @property
    def architecture(self):
        return platform.machine()

    @property
    def platform(self):
        return platform.platform()

    @property
    def os(self):
        return platform.system()

    @property
    def ip(self):
        return None

    @property
    def hostname(self):
        return platform.node() if platform.node() else socket.gethostname()

    @property
    def datetime(self):
        return datetime.datetime.now()

    @staticmethod
    def _getvaluefromlsb(compared):
        res = ""
        f = open("/etc/lsb-release", "r")
        for line in f.readlines():
            key, val = line.replace("\n", "").replace("\r", "").split('=')
            if key == compared:
                res = val.replace("\"", "")
        f.close()
        return res

    @property
    def distribName(self):
        return self._getvaluefromlsb("DISTRIB_DESCRIPTION")

    @property
    def distribId(self):
        return self._getvaluefromlsb("DISTRIB_ID")

    def __str__(self):
        _substr = ""
        _substr += "Hostname:\t\t" + self.hostname + "\n"
        _substr += "OS:\t\t\t\t" + self.os + " (" + self.distribId + ")" + "\n"
        _substr += "Distrib name:\t" + self.distribName + "\n"
        _substr += "Version:\t\t" + self.version + "\n"
        _substr += "Architecture:\t" + self.architecture + "\n"
        _substr += "Platform:\t\t" + self.platform + "\n"
        _substr += "DateTime:\t\t" + str(self.datetime) + "\n"
        return _substr

