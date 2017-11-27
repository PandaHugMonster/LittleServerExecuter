#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
from Lse import ServiceManager

class Service:

	_manager = None
	_systemd = None
	_switches = []

	_key = None
	_label = None
	_switches_service_lock = False

	def __init__(self, manager: ServiceManager, key: str, label: str=None):
		self._manager = manager
		self._systemd = manager.systemd
		self._key = key

		if not label:
			label = self._systemd.get_property(key, 'Description')

		self._label = label

	@property
	def key(self):
		return self._key

	@property
	def label(self):
		return self._label

	@property
	def status(self):
		return self._systemd.get_property(self.key, 'ActiveState') == 'active'

	@status.setter
	def status(self, value: bool):
		if value:
			self._systemd.startService(self.key)
		else:
			self._systemd.stopService(self.key)

	def sig_event_stop(self):
		status = self.status
		print('Service [' + self.key + '] changed status from "' + str(not status) + '" to "' + str(status) + '"')
		self._manager.service_event_status_changed(self, status)