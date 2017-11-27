#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
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
	_viewpoint = None
	systemd = None
	service_manager = None
	_is_permission_needed = True
	_services_completed = None
	_stack = None
	_conf_path = None
	_conf = {}
	switches_service_lock = False
	protected_widgets = []
	all_services = []

	subpage_switcher = None
	search_button = None

	def __init__(self):
		name = "page_systemd"
		title = _("SystemD Control")
		self._conf_path = FileAccessHelper.get_settings_path("services")
		self._conf = FileAccessHelper.load_settings(self._conf_path)
		super().__init__(name, title)

	def attach_init(self, page_manager: PageManager):
		super().attach_init(page_manager)

		self.systemd = Systemd(page_manager.dbus, page_manager.polkit_helper)
		self.service_manager = ServiceManager(self.systemd)
		self._setup_header_elements()
		self._insert_all_services()

	@property
	def conf(self):
		return self._conf

	def _insert_all_services(self):
		units = self.systemd.listUnits()

		for key in units:
			if '_show_only' not in self.conf or key in self.conf['_show_only']:
				self.service_manager.add_service(key)

	def _setup_header_elements(self):
		self._stack = Gtk.Stack()
		self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		self.subpage_switcher = Gtk.StackSwitcher()
		self.subpage_switcher.set_stack(self._stack)

		icon = Gtk.Image()
		icon.set_from_icon_name("edit-find-symbolic", Gtk.IconSize.MENU)
		self.search_button = Gtk.ToggleButton()
		self.search_button.add(icon)
		self.search_button.connect("toggled", self._on_search_toggled)
		self.search_button.props.valign = Gtk.Align.CENTER

	def permission_granted_callback(self, status: bool):
		for widget in self.protected_widgets:
			widget.set_sensitive(status)

	@property
	def get_main_container(self) -> Gtk.Box:
		return self._stack

	def _callback_grid_services_all(self, grid: Gtk.Grid, row_index: int, service: Service):
		switch = Gtk.Switch()
		spinner = Gtk.Spinner()

		grid.attach(spinner, 0, row_index, 1, 1)
		grid.attach(switch, 1, row_index, 1, 1)
		grid.attach(Gtk.Label(label=service.key, xalign=0), 2, row_index, 1, 1)
		grid.attach(Gtk.Label(label=service.label, xalign=0), 3, row_index, 1, 1)

		self.service_manager.attach_switch(service.key, switch)
		return row_index + 1

	def all_services_show(self):

		scrolled_window = Gtk.ScrolledWindow()
		sub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		grid = self._make_default_grid(scrolled_window, sub_box, True)

		services = self.service_manager.get_all(self.conf['excluded'])
		self.build_grid_services(grid, services, self._callback_grid_services_all)

		return scrolled_window

	""" // """
	def _callback_grid_services_groups(self, grid: Gtk.Grid, row_index: int, service: Service):
		switch = Gtk.Switch()
		spinner = Gtk.Spinner()

		# grid.attach(Gtk.Label(label='Group 1', xalign=0), 0, row_index, 4, 1)
		# row_index += 1

		grid.attach(spinner, 0, row_index, 1, 1)
		grid.attach(switch, 1, row_index, 1, 1)
		grid.attach(Gtk.Label(label=service.key, xalign=0), 2, row_index, 1, 1)
		grid.attach(Gtk.Label(label=service.label, xalign=0), 3, row_index, 1, 1)

		self.service_manager.attach_switch(service.key, switch)
		return row_index + 1

	def groups_show(self):

		scrolled_window = Gtk.ScrolledWindow()
		sub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		grid = self._make_default_grid(scrolled_window, sub_box, True)

		services = self.service_manager.get_all(self.conf['excluded'])
		self.build_grid_services(grid, services, self._callback_grid_services_groups)

		return scrolled_window

	def _make_default_grid(self, scrolled_window:Gtk.ScrolledWindow, sub_box: Gtk.Box=None, is_protected=True):

		if not sub_box:
			sub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		grid = Gtk.Grid()
		scrolled_window.add(sub_box)
		if is_protected:
			self.protected_widgets.append(sub_box)

		sub_box.add(grid)

		grid.set_border_width(20)
		grid.set_row_spacing(15)
		grid.set_column_spacing(20)
		grid.get_style_context().add_class("lse-grid")

		return grid

	def _on_search_toggled(self):
		pass

	def build_grid_services(self, grid: Gtk.Grid, services: OrderedDict, callback: callable, row_index: int=0):
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
		self._stack.add_titled(self.groups_show(), 'grouped_services', _("Grouped"))
		self._stack.add_titled(self.all_services_show(), 'all_services', _("All services"))

	def apply_header(self, header:Gtk.HeaderBar):
		header.pack_start(self.search_button)
		header.set_custom_title(self.subpage_switcher)
