#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

import dbus


class PolkitAuth:
    dbus = None
    appPid = None

    polkitAuthInterface = None

    subject = None

    granted = False
    tempId = None

    def __init__(self, dbus, pid):
        self.dbus = dbus
        self.appPid = pid

        polkitAuthObject = self.dbus.getObject(
            'org.freedesktop.PolicyKit1',
            '/org/freedesktop/PolicyKit1/Authority')

        self.polkitAuthInterface = self.dbus.getInterface(
            polkitAuthObject,
            dbus_interface='org.freedesktop.PolicyKit1.Authority')

    def grantAccess(self, action, details={}, flags=1, cancellable=''):
        self.subject = ('unix-process', {
            'pid': dbus.UInt32(self.appPid, variant_level=1),
            'start-time': dbus.UInt64(0, variant_level=1)})
        (self.granted, other, details) = self.polkitAuthInterface.CheckAuthorization(
            self.subject,
            action,
            details,
            flags,
            cancellable)

        self.tempId = details.get('polkit.temporary_authorization_id')

        return self.granted

    def revokeAccess(self):
        if self.subject:
            self.polkitAuthInterface.RevokeTemporaryAuthorizationById(self.tempId)
            self.granted = False
