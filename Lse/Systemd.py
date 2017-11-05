#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import array


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
		self.dbus.attachEvent(handler, jobtype, self.OBJ_NAME_MANAGER, self.OBJ_NAME, self.OBJ_PATH)

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

	def listUnits(self):
		return self.manager.ListUnits()

	def _get_properties_interface(self, unit_name: str):
		unit_interface = self.manager.GetUnit(unit_name)
		objected = self.dbus.getObject(self.OBJ_NAME, unit_interface)
		sub = self.dbus.getInterface(objected, 'org.freedesktop.DBus.Properties')
		return sub

	def get_property(self, unit_name: str, property: str):
		sub = self._get_properties_interface(unit_name)
		return sub.Get("org.freedesktop.systemd1.Unit", property)

	def get_properties(self, unit_name: str, properties: array = []):
		sub = self._get_properties_interface(unit_name)
		unit_props = sub.GetAll("org.freedesktop.systemd1.Unit")
		res = {}
		for key in unit_props:
			_key = str(key)
			if not properties or (_key in properties):
				res[_key] = unit_props[key]
		return res

	def get_service_common_info(self, unit_name: str):
		keys = ["Description", "Id", "ActiveState", "Names"]
		props = self.get_properties(unit_name, keys)
		return props

	def errorHappened(self, e):
		print(e)

	def loadUnit(self, service):
		return self.manager.LoadUnit(service)
