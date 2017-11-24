#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
from abc import ABCMeta, abstractmethod

import gi

from Lse import PageManager

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk


class AbstractPage:
	__metaclass__ = ABCMeta

	_name = None
	_title = None
	_content = None
	_page_manager = None
	_is_permission_needed = False

	def __init__(self, name, title):
		self._name = name
		self._title = title

	@property
	def page_manager(self) -> PageManager:
		return self._page_manager

	@page_manager.setter
	def page_manager(self, val: PageManager):
		self._page_manager = val

	@property
	def content(self) -> Gtk.Container:
		if not self._content:
			self._content = self.prepare_content
		return self._content

	@property
	def prepare_content(self) -> Gtk.Container:
		box = self.get_main_container
		self.set_defaults(box)
		return box

	@property
	@abstractmethod
	def get_main_container(self) -> Gtk.Box:
		pass

	def set_defaults(self, box: Gtk.Box):
		pass

	@property
	def title(self):
		return self._title

	@property
	def name(self):
		return self._name

	@property
	def is_permission_needed(self):
		return self._is_permission_needed

	def permission_granted_callback(self, status:bool):
		pass

	def attach_init(self, page_manager:PageManager):
		self.page_manager = page_manager

		if self.is_permission_needed:
			page_manager.attach_permission_callback(self.permission_granted_callback)

	def apply_header(self, header:Gtk.HeaderBar):
		header.set_title(self.title)
