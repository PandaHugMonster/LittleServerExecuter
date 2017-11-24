#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import array
import os
from collections import OrderedDict

from Lse.Systemd import Systemd
from Lse.models import Service as ServiceModule


class ServiceManager:

	_systemd = None
	_services = {}

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
		in_code_excluded = ['-.mount', 'systemd-hostnamed.service']
		if key not in in_code_excluded:
			return self.get_service(key)

		return None

	def get_all(self, excluded=None) -> OrderedDict:
		res = OrderedDict()
		in_code_excluded = [ '-.mount', 'systemd-hostnamed.service' ]
		i = 0
		services = OrderedDict(sorted(self._services.items(), key=lambda t: t[0].lower()))
		for key in services:
			if i < 10 and (not excluded or key not in excluded) and (key not in in_code_excluded):
				res[key] = services[key]
				i += 1

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
