#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

import dbus
from dbus import SystemBus


class DBus:
    cachedbus = None

    @property
    def bus(self):
        return self.cachedbus

    def __init__(self):
        self.cachedbus = SystemBus()

    def getObject(self, name, path):
        return self.cachedbus.get_object(bus_name=name, object_path=path)

    def getInterface(self, obj, dbus_interface):
        return dbus.Interface(obj, dbus_interface)

    def attachEvent(self,
                    handler_function,
                    signal_name=None,
                    dbus_interface=None,
                    bus_name=None,
                    path=None,
                    **keywords):
        self.cachedbus.add_signal_receiver(
            handler_function,
            signal_name,
            dbus_interface,
            bus_name,
            path,
            **keywords)
