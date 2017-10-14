#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import datetime
import platform
import socket

from pathlib import Path

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
        lsb_path = "/etc/lsb-release"

        if Path(lsb_path).is_file():
            f = open(lsb_path, "r")
            for line in f.readlines():
                key, val = line.replace("\n", "").replace("\r", "").split('=')
                if key == compared:
                    res = val.replace("\"", "")
            f.close()
        else:
            res = "LSB File is not found: \"%s\"" % lsb_path


        return res

    @property
    def distribName(self):
        return self._getvaluefromlsb("DISTRIB_DESCRIPTION")

    @property
    def distribId(self):
        return self._getvaluefromlsb("DISTRIB_ID")

    def __str__(self):
        substr = ""
        substr += "Hostname:\t\t" + self.hostname + "\n"
        substr += "OS:\t\t\t\t" + self.os + " (" + self.distribId + ")" + "\n"
        substr += "Distrib name:\t" + self.distribName + "\n"
        substr += "Version:\t\t" + self.version + "\n"
        substr += "Architecture:\t" + self.architecture + "\n"
        substr += "Platform:\t\t" + self.platform + "\n"
        substr += "DateTime:\t\t" + str(self.datetime) + "\n"
        return substr

