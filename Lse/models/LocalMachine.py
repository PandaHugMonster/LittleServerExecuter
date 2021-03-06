#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import datetime
import platform
import socket
import json

from pathlib import Path

from Lse.helpers import FileAccessHelper
from Lse.models import AbstractMachine


class LocalMachine(AbstractMachine):

    @property
    def type(self):
        return "Local"

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
    def distrib_name(self):
        return self._getvaluefromlsb("DISTRIB_DESCRIPTION")

    @property
    def distrib_id(self):
        return self._getvaluefromlsb("DISTRIB_ID")

    @property
    def logo_path(self):
        return FileAccessHelper.get_logo(self.distrib_id)

    @property
    def settings_path(self):
        return FileAccessHelper.get_settings_path()

    _settings = None

    @property
    def settings(self):
        if not self._settings:
            print("Settings loaded from: " + self.settings_path)
            json_data = open(self.settings_path)
            self._settings = json.load(json_data)
            json_data.close()

        return self._settings

    @settings.setter
    def settings(self, value):
        pass

    def __str__(self):
        substr = ""
        substr += "Hostname:\t\t" + self.hostname + "\n"
        substr += "OS:\t\t\t\t" + self.os + " (" + self.distrib_id + ")" + "\n"
        substr += "Distrib name:\t" + self.distrib_name + "\n"
        substr += "Version:\t\t" + self.version + "\n"
        substr += "Architecture:\t" + self.architecture + "\n"
        substr += "Platform:\t\t" + self.platform + "\n"
        substr += "DateTime:\t\t" + str(self.datetime) + "\n"
        substr += "Settings:\t\t" + self.settings_path + "\n"
        substr += "Logo:\t\t\t" + self.logo_path + "\n"
        return substr

