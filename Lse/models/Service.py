#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
from Lse import ServiceManager
from gi.repository import Gtk


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

	def attach_switch(self, switch: Gtk.Switch):
		self._switches.append(switch)
		switch.set_state(self.status)
		switch.connect("notify::active", self.switch_event_status_changed)

	def _preserved_switch(self, switch, state):
		self._switches_service_lock = True
		print('Switch State changed: ' + str(state))
		switch.set_state(state)
		self._switches_service_lock = False

	def switch_event_status_changed(self, switch: Gtk.Switch, property):
		status = self.status
		substatus = bool(switch.get_active())
		if status != substatus:
			if substatus:
				self._systemd.startService(self.key)
				print('Starting. [' + self.key + ']')
			else:
				self._systemd.stopService(self.key)
				print('Stopping. [' + self.key + ']')
		else:
			print('Not changed. [' + self.key + ']')

	@property
	def key(self):
		return self._key

	@property
	def label(self):
		return self._label

	@property
	def status(self):
		return self._systemd.get_property(self.key, 'ActiveState') == 'active'

	def sig_event_stop(self):
		status = self.status
		print('Service [' + self.key + '] changed status from "' + str(not status) + '" to "' + str(status) + '"')

		self._all_switches_change()

	def _all_switches_change(self):
		status = self.status
		print(self._switches)
		if self._switches:
			for switch in self._switches:
				if switch.get_active() != status:
					self._preserved_switch(switch, status)
