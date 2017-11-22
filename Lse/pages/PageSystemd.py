#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import datetime
import html
import gettext
import os
from collections import OrderedDict

from gi.repository import Gtk

from Lse.AbstractPage import AbstractPage
from Lse.PageManager import PageManager
from Lse.ServiceManager import ServiceManager
from Lse.Systemd import Systemd
from Lse.helpers import FileAccessHelper
from Lse.models.Service import Service

localedir = os.path.join(FileAccessHelper.work_directory(), 'locale')
translate = gettext.translation("pages", localedir)
_ = translate.gettext


class PageSystemd(AbstractPage):

	grid = None
	notebook = None
	systemd = None
	service_manager = None
	_is_permission_needed = True
	_services_completed = None
	switches_service_lock = False
	protected_widgets = []
	all_services = []

	def __init__(self):
		name = "page_systemd"
		title = _("SystemD Control")
		super().__init__(name, title)

	def attach_init(self, page_manager: PageManager):
		super().attach_init(page_manager)
		self.systemd = Systemd(page_manager.dbus, page_manager.polkit_helper)
		self.service_manager = ServiceManager(self.systemd)
		self._insert_all_services()

	def _insert_all_services(self):
		units = self.systemd.listUnits()

		for key in units:
			self.service_manager.add_service(key)

	def permission_granted_callback(self, status: bool):
		for widget in self.protected_widgets:
			widget.set_sensitive(status)

	@property
	def get_main_container(self) -> Gtk.Box:
		if not self.notebook:
			self.notebook = Gtk.Notebook.new()
		return self.notebook

	# def groups_show(self):
	# 	self.grid = Gtk.Grid()
	# 	sw = Gtk.ScrolledWindow()
	# 	sw.add(self.grid)
	#
	# 	self.grid.set_border_width(20)
	# 	self.grid.set_row_spacing(15)
	# 	self.grid.set_column_spacing(20)
	# 	self.grid.get_style_context().add_class("lse-grid")
		# builder.get_object("place_kernel").set_text(machine.version)
		# self.build_table()
		# return sw

	# def all_services_list(self) -> OrderedDict:
	# 	listy = self.systemd.listUnits()
	# 	res = {}
	#
	# 	for item in listy:
	# 		sub = self.systemd.get_service_common_info(item)
	# 		res[sub['Id']] = " [ <b>" + sub['Id'] + "</b> ] " + html.escape(sub['Description'])
	#
	# 	return OrderedDict({'All Services': res})

	def callback_rb_all_services(self, grid: Gtk.Grid, row_index: int, service: Service):
		switch = Gtk.Switch()
		spinner = Gtk.Spinner()

		grid.attach(spinner, 0, row_index, 1, 1)
		grid.attach(switch, 1, row_index, 1, 1)
		grid.attach(Gtk.Label(label=service.label, xalign=0), 2, row_index, 1, 1)
		grid.attach(Gtk.Label(label=service.key, xalign=0), 3, row_index, 1, 1)

		service.attach_switch(switch)
		return row_index + 1

	def all_services_show(self):

		grid = Gtk.Grid()
		sw = Gtk.ScrolledWindow()
		sw.add(grid)
		self.protected_widgets.append(grid)

		grid.set_border_width(20)
		grid.set_row_spacing(15)
		grid.set_column_spacing(20)
		grid.get_style_context().add_class("lse-grid")

		# self.all_services = self.build_grid(all_services_list)
		# self.build_table(self.all_services, grid)
		services = self.service_manager.get_all()
		# key = 'httpd.service'
		# services = OrderedDict({ key: self.service_manager.get_service(key) })
		self.build_grid_services(grid, services, self.callback_rb_all_services)

		return sw

	def build_grid_services(self, grid: Gtk.Grid, services: OrderedDict, callback: callable):
		row_index = 0
		for key in services:
			if type(services[key]) == Service:
				row_index = callback(grid, row_index, services[key])
			elif type(services[key]) == OrderedDict:
				group = key
				for subkey in services[group]:
					service = services[group][subkey]

					group_label = Gtk.Label(label=group)
					box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

					stop_all_button = Gtk.Button.new_from_icon_name("media-playback-stop", Gtk.IconSize.BUTTON)
					stop_all_button.group = group

					start_all_button = Gtk.Button.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
					start_all_button.group = group

					# start_all_button.connect("clicked", lambda widget: self.process_group_services_now(True, widget.group))
					# stop_all_button.connect("clicked", lambda widget: self.process_group_services_now(False, widget.group))

					# self.protected_widgets.append(start_all_button)
					# self.protected_widgets.append(stop_all_button)

					box.add(start_all_button)
					box.add(stop_all_button)

					grid.attach(group_label, 0, row_index, 1, 1)
					row_index += 1

					grid.attach(box, 1, row_index, 1, 1)
					row_index += 1

					row_index = callback(grid, row_index, service)

	def set_defaults(self, box: Gtk.Box):
		# self.notebook.append_page(self.groups_show(), Gtk.Label(label=_("Grouped")))
		self.notebook.append_page(self.all_services_show(), Gtk.Label(label=_("All services")))

	# def __old_build_grid(self, sub_services=None):
	# 	if not sub_services:
	# 		sub_services = self.page_manager.machine.settings['services']
	#
	# 	services = {}
	# 	for (group, datag) in sub_services.items():
	# 		services[group] = {}
	# 		datag = OrderedDict(sorted(datag.items(), key=lambda t: t[0].lower()))
	# 		for (service, title) in datag.items():
	# 			try:
	# 				state = self.systemd.get_property(service, 'ActiveState')
	# 			except DBusException:
	# 				state = "inactive"
	# 				print("NOTL: :( %s" % service)
	#
	# 			services[group][service] = {
	# 				'title': str(title),
	# 				'state': str(state),
	# 				'switch': Gtk.Switch(),
	# 				'spinner': Gtk.Spinner(),
	# 			}
	# 	return services
	#
	# def get_services_completed(self):
	# 	if not self._services_completed:
	# 		self._services_completed = self.build_grid_services()
	# 	return self._services_completed

	# def build_table(self, services=None, grid=None):
	# 	if not grid:
	# 		grid = self.grid
	#
	# 	if not services:
	# 		services = self.get_services_completed()
	#
	# 	if services:
	# 		prev = None
	# 		keys = list(sorted(services.keys()))
	# 		for group in keys:
	# 			datag = services[group]
	#
	# 			group_name = Gtk.Label(label=group)
	# 			box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	#
	# 			if self.uid == 0:
				# stop_all_button = Gtk.Button.new_from_icon_name("media-playback-stop", Gtk.IconSize.BUTTON)
				# start_all_button = Gtk.Button.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
				# start_all_button.group = group
				# stop_all_button.group = group
				#
				# start_all_button.connect("clicked", lambda widget: self.process_group_services_now(True, widget.group))
				# stop_all_button.connect("clicked", lambda widget: self.process_group_services_now(False, widget.group))
				#
				# self.protected_widgets.append(start_all_button)
				# self.protected_widgets.append(stop_all_button)
				#
				# box.add(start_all_button)
				# box.add(stop_all_button)
				#
				# if not prev:
				# 	grid.add(group_name)
				# else:
				# 	grid.attach_next_to(group_name, prev, Gtk.PositionType.BOTTOM, 1, 1)
				# grid.attach_next_to(box, group_name, Gtk.PositionType.RIGHT, 1, 1)
				# prepre = None
				# for (service, data) in datag.items():
				# 	switch = data['switch']
				# 	spinner = data['spinner']
				# 	switch.set_active(data['state'] == 'active')
				# 	switch.connect("notify::active", self.work_with_service, services)
				# 	self.protected_widgets.append(switch)
				# 	label = Gtk.Label(label=data['title'], xalign=0)
				# 	label.set_use_markup(True)
				#
				# 	if not prepre:
				# 		prepre = True
				# 		grid.attach_next_to(switch, group_name, Gtk.PositionType.BOTTOM, 1, 1)
				# 	else:
				# 		grid.attach_next_to(switch, prev, Gtk.PositionType.BOTTOM, 1, 1)
				# 	grid.attach_next_to(label, switch, Gtk.PositionType.RIGHT, 1, 1)
				# 	grid.attach_next_to(spinner, label, Gtk.PositionType.RIGHT, 1, 1)
				# 	prev = switch
	#
	# def process_group_services_now(self, action, group_name):
	# 	services = self.get_services_completed()
	# 	for (group, gdata) in services.items():
	# 		if group == group_name:
	# 			for (service, data) in gdata.items():
	# 				if data['switch'].get_active() != action:
	# 					data['switch'].set_active(action)
	#
	# def preserved_switch(self, switcher, state):
		# self.switches_service_lock = True
		# switcher.set_state(state)
		# self.switches_service_lock = False
		# pass

	# def work_with_service(self, switch, x, services=None):
	#
	# 	if not services:
	# 		services = self.get_services_completed()
	#
	# 	if not self.switches_service_lock:
	# 		for (group, datag) in services.items():
	# 			for (service, data) in datag.items():
	# 				if data['switch'] is switch:
	# 					data["spinner"].start()
	# 					data['lastactiontime'] = datetime.datetime.now()
	# 					last = data["lastactiontime"]
	#
	# 					prev_state = switch.get_active()
	# 					if prev_state:
	# 						print("Systemd Start executed [%s]" % service)
	# 						self.systemd.startService(service)
	# 					else:
	# 						print("Systemd Stop executed [%s]" % service)
	# 						self.systemd.stopService(service)
	#
	# def systemd_job_removed(self, arg1, path, service, status):
	# 	for (group, datag) in self.all_services.items():
	# 		for (servicein, data) in datag.items():
	# 			spinner = data["spinner"]
	# 			if servicein == service:
	# 				if status == 'done':
	# 					spinner.stop()
	# 					res = self.systemd.get_property(servicein, 'ActiveState')
	# 					if res == 'active':
	# 						self.preserved_switch(data['switch'], True)
	# 					else:
	# 						self.preserved_switch(data['switch'], False)
