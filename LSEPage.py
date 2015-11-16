#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, Gio, Gdk, GObject, GdkPixbuf


class LSEPage:

	widgets = {}

	@property
	def header(self):
		return self._header
	@property
	def content(self):
		return self._content
	@property
	def name(self):
		return self._name
	@property
	def title(self):
		return self._title
	@name.setter
	def name(self, value):
		self._name = value
	@title.setter
	def title(self, value):
		self._title = value
	@header.setter
	def header(self, value):
		self._header = value
	@content.setter
	def content(self, value):
		self._content = value

	def __init__(self, content = None, name = None, title = None):
		if content:
			self._content = content

		if name:
			self._name = name

		if title:
			self._title = title
