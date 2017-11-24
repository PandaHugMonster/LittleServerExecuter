#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import gi

from Lse import AbstractPage, PolkitAuth
from Lse.DBus import DBus
from Lse.models.AbstractMachine import AbstractMachine

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk


class PageManager:

	_app = None
	_header = None
	_machine = None

	_polkit_helper = None
	_dbus = None
	_main_view = None
	_stack = None
	_sidebar = None
	_sidebar_listbox = None

	_name_index = {}
	_pages = []

	def __init__(self, machine: AbstractMachine, app):
		self._app = app
		self._header = Gtk.HeaderBar()
		self._machine = machine
		self._main_view = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self._stack = Gtk.Stack()

		# self.recompose_ui("systemd")

		self._main_view.pack_start(self.side_bar, False, False, 0)
		self._main_view.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
		self._main_view.pack_start(self.main_content, True, True, 0)

	@staticmethod
	def list_header_func(row, before, user_data):
		if before and not row.get_header():
			row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

	@property
	def main_content(self):
		self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
		return self._stack

	def change_viewpoint(self, list, row):
		if isinstance(row, Gtk.ListBoxRow):
			self._stack.set_visible_child_name(row.childname)
			self.recompose_ui(row.childname)

	def recompose_ui(self, name):
		page = self.get_page(name)
		for child in self.header.get_children():
			self.header.set_custom_title(None)
			self.header.set_title(None)
			self.header.remove(child)
		page.apply_header(self.header)
		self.header.show_all()

		self._app.window.queue_draw()

	@property
	def side_bar(self):
		if not self._sidebar:
			box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
			listbox = Gtk.ListBox()
			listbox.get_style_context().add_class("lse-sidebar")
			listbox.set_size_request(250, -1)
			listbox.connect("row-selected", self.change_viewpoint)
			listbox.set_header_func(self.list_header_func, None)
			self._sidebar_listbox = listbox

			scroll = Gtk.ScrolledWindow()
			scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
			scroll.add(listbox)
			box.pack_start(scroll, True, True, 0)

			self._sidebar = box

		return self._sidebar

	@property
	def viewpoint(self):
		return self._main_view

	@property
	def dbus(self):
		return self._dbus

	@property
	def polkit_helper(self):
		return self._polkit_helper

	def set_extra_libs(self, dbus:DBus, polkit:PolkitAuth):
		self._dbus = dbus
		self._polkit_helper = polkit

	def _add_page_to_index(self, page: AbstractPage):
		size = len(self._pages)

		self._pages.insert(size, page)
		self._name_index[page.name] = size
		self._stack.add_named(page.content, page.name)

		row = Gtk.ListBoxRow()
		row.get_style_context().add_class("lse-sidebar-row")
		row.add(Gtk.Label(label=page.title))
		row.childname = page.name

		self._sidebar_listbox.add(row)

	def add_page(self, page: AbstractPage) -> bool:
		size = len(self._pages)
		name = page.name

		if size:
			for name_from_index in self._name_index:
				if name == name_from_index:
					return True

		page.attach_init(self)
		self._add_page_to_index(page)

		return True

	@property
	def machine(self) -> AbstractMachine:
		return self._machine

	@property
	def header(self) -> Gtk.HeaderBar:
		return self._header

	@property
	def pages(self) -> list:
		return self._pages

	def get_page(self, name: str) -> AbstractPage:
		index = self._name_index[name]
		return self._pages[index]

	@property
	def builder(self) -> Gtk.Builder:
		return self._app.builder

	def attach_permission_callback(self, callback):
		self._app.attach_permission_callback(callback)