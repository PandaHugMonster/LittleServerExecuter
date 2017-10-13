#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4


class Systemd:
    ACTION_MANAGE_UNITS = "org.freedesktop.systemd1.manage-units"

    JOB_REMOVED = 'JobRemoved'
    OBJ_NAME = 'org.freedesktop.systemd1'
    OBJ_PATH = '/org/freedesktop/systemd1'
    OBJ_NAME_MANAGER = 'org.freedesktop.systemd1.Manager'

    dbus = None
    objected = None
    cachedmanager = None
    polkit = None

    def __init__(self, dbus, polkit):
        self.dbus = dbus
        self.polkit = polkit
        self.objected = self.dbus.getObject(self.OBJ_NAME, self.OBJ_PATH)

    @property
    def manager(self):
        if not self.cachedmanager:
            self.cachedmanager = self.dbus.getInterface(self.objected, self.OBJ_NAME_MANAGER)
        return self.cachedmanager

    def subscribe(self):
        self.manager.Subscribe()

    def signalReceiver(self, handler, jobtype=JOB_REMOVED):
        self.subscribe()
        self.dbus.attachEvent(handler,
                              jobtype,
                              self.OBJ_NAME_MANAGER,
                              self.OBJ_NAME,
                              self.OBJ_PATH)

    def startService(self, service, errorHandler=None):
        if not errorHandler:
            errorHandler = self.errorHappened

        if self.polkit.granted:
            try:
                self.manager.StartUnit(service, 'replace')
                allGood = True
            except:
                errorHandler('Error, probably non-auth; Start rejected')
                allGood = False

            return allGood
        else:
            if self.polkit.grantAccess(self.ACTION_MANAGE_UNITS):
                return self.startService(service, errorHandler)

        return False

    def stopService(self, service, errorHandler=None):
        if not errorHandler:
            errorHandler = self.errorHappened

        if self.polkit.granted:
            try:
                self.manager.StopUnit(service, 'replace')
                allGood = True
            except:
                errorHandler('Error, probably non-auth; Stop rejected')
                allGood = False

            return allGood
        else:
            if self.polkit.grantAccess(self.ACTION_MANAGE_UNITS):
                return self.startService(service, errorHandler)

        return False

    def errorHappened(self, e):
        print(e)

    def loadUnit(self, service):
        return self.manager.LoadUnit(service)
