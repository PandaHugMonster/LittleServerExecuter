#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import array
import os
from collections import OrderedDict

from gi.repository import Gtk

from Lse.Systemd import Systemd
from Lse.models import Service as ServiceModule


class ServiceManager:

	_systemd = None
	_services = {}
	_switches = {}
	_switches_service_lock = False

	def __init__(self, systemd: Systemd):
		self._systemd = systemd
		self.systemd.subscribe()
		self.systemd.signalReceiver(self.signal_receiver_job_removed, Systemd.SIG_JOB_REMOVED)
		# self.systemd.signalReceiver(self.signal_receiver_job_new, Systemd.SIG_JOB_NEW)

	@property
	def systemd(self):
		return self._systemd

	def add_service(self, key: str):
		if key not in self._services:
			self._services[key] = ServiceModule.Service(self, key)

	def remove_service(self, key: str):
		if key in self._services:
			del self._services[key]

	def get_service(self, key: str) -> ServiceModule or None:
		key = str(key)
		if key in self._services:
			return self._services[key]

		return None

	def get_if_not_excluded_service(self, key: str) -> ServiceModule or None:
		return self.get_service(key)

	def get_all(self, excluded=None) -> OrderedDict:
		res = OrderedDict()
		services = OrderedDict(sorted(self._services.items(), key=lambda t: t[0].lower()))
		for key in services:
			if not excluded or key not in excluded:
				res[key] = services[key]

		return res

	def get_only(self, included: list) -> OrderedDict:
		res = OrderedDict()
		services = OrderedDict(sorted(self._services.items(), key=lambda t: t[0].lower()))
		for key in services:
			if key in included:
				res[key] = services[key]

		return res

	def get_only_type(self, types: array) -> OrderedDict:
		res = OrderedDict()
		services = OrderedDict(sorted(self._services.items(), key=lambda t: t[0].lower()))
		for key in services:
			filename, file_extension = os.path.splitext(key)
			if file_extension[1:] in types:
				res[key] = services[key]

		return res

	def signal_receiver_job_removed(self, arg1, path, key, status):
		service = self.get_if_not_excluded_service(key)
		if service and status == 'done':
			service.sig_event_stop()

	def signal_receiver_job_new(self, arg1, path, key, status):
		service = self.get_if_not_excluded_service(key)
		if service and status == 'done':
			service.sig_event_start()

	def attach_switch(self, key: str, switch: Gtk.Switch):
		if key not in self._switches:
			self._switches[key] = []
		if switch not in self._switches[key]:
			self._switches[key].append(switch)

			service = self.get_service(key)
			switch.set_state(service.status)
			switch.connect("notify::active", self.switch_event_status_changed, key)

	def attach_group_change(self, button, status, services):
		for index in services:
			button.connect("clicked", self.change_service_status, services[index], status)

	def change_service_status(self, button, service, status):
		service.status = status

	def _preserved_switch(self, switch, state):
		self._switches_service_lock = True
		print('Switch State changed: ' + str(state))
		switch.set_state(state)
		self._switches_service_lock = False

	def service_event_status_changed(self, service: ServiceModule, status: bool):
		print('__SERVICE_EVENT')

		if service.key in self._switches:
			for switch in self._switches[service.key]:
				self._preserved_switch(switch, service.status)

	def switch_event_status_changed(self, switch: Gtk.Switch, param: str, key: str):
		service = self.get_service(key)
		if not self._switches_service_lock:
			print('__SWITCH_EVENT happened')
			status = service.status
			substatus = bool(switch.get_active())
			if status != substatus:
				if substatus:
					service.status = True
					print('Starting. [' + service.key + ']')
				else:
					service.status = False
					print('Stopping. [' + service.key + ']')
			else:
				print('Not changed. [' + service.key + ']')
		else:
			print('__SWITCH_EVENT blocked')
