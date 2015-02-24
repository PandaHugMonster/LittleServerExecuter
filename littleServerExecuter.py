#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan@newnauka.org>
# Version: 0.4

import os
import sys
import re
import json
import time
from threading import Thread
from gi.repository import Gtk, Gio
from random import randint
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

from dbus import SystemBus, SessionBus, Interface
import gobject

currentDirectory = os.path.dirname(os.path.abspath(__file__))

bus = SystemBus()
systemd = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')

class LittleServerExecuterApp(Gtk.Application):
	""" Settings file """
	settingsFile = "settings.json"

	""" SystemD Manager """
	manager = None

	""" Application Pid Number """
	pid = None
	""" List of switchers """
	switchers = None
	""" List of srvices through dbus """
	services = None
	""" Settings """
	settings = None
	""" Gtk Window Object """
	window = None
	""" GtkBuilder Object """
	builder = None
	
	""" Main Grid """
	grid = None

	""" Constructor """
	def __init__(self):
		self.pid = str(os.getpid())
		Gtk.Application.__init__(self)
	
	""" Gtk.Application Startup """
	def do_startup(self):
		Gtk.Application.do_startup(self)
		
		menu = Gio.Menu()
		menu.append("О программе", "app.about")
		menu.append("Выйти", "app.quit")
		self.set_app_menu(menu)
		
		aboutAction = Gio.SimpleAction.new("about", None)
		aboutAction.connect("activate", self.appAbout)
		self.add_action(aboutAction)
		
		quitAction = Gio.SimpleAction.new("quit", None)
		quitAction.connect("activate", self.appExit)
		self.add_action(quitAction)
		
		self.manager.Subscribe()
	
	"""	Activation """
	def do_activate(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file(currentDirectory + '/face.ui')

		self.window = self.builder.get_object("TheWindow")
		self.grid = self.builder.get_object("switchersGrid")
		handlers = { "appExit": self.appExit }
		self.builder.connect_signals(handlers)
			
		self.setSettings()
	
		
		
		self.add_window(self.window)
		self.window.show_all()

	def startService(self, service):
		self.manager.StartUnit(service, 'replace')
		
	def stopService(self, service):
		self.manager.StopUnit(service, 'replace')
		

	""" Get settings """
	def setSettings(self):
		json_data = open(currentDirectory + "/" + self.settingsFile)
		self.settings = json.load(json_data)
		json_data.close()
		self.services = {}
		for (service, title) in self.settings['services'].items():
			service_unit = self.manager.LoadUnit(service)
			service_interface = bus.get_object('org.freedesktop.systemd1', str(service_unit))
			state = service_interface.Get('org.freedesktop.systemd1.Unit',
				'ActiveState',
				dbus_interface='org.freedesktop.DBus.Properties')
			self.services[service] = {
				'unit': service_unit,
				'interface': service_interface,
				'title': title,
				'state': state,
				'switch': Gtk.Switch()
			}
			print("%s = %s | %s" % (service, title, state))
		
		self.buildTable()
		
	def buildTable(self):
		prev = None
		for (service, data) in self.services.items():
			switch = data['switch']
			switch.connect("notify::active", self.on_switch_activated)
			label = Gtk.Label(data['title'])
			
			if not prev:
				self.grid.add(switch)
			else:
				self.grid.attach_next_to(switch, prev, Gtk.PositionType.BOTTOM, 1, 1)
			self.grid.attach_next_to(label, switch, Gtk.PositionType.RIGHT, 1, 1)
			prev = switch

	def on_switch_activated(self, switch, data):
		for (service, data) in self.services.items():
			if data['switch'] is switch:
				print(service)
		

	""" Run App About """
	def appAbout(self, action, parameter):
		aboutwindow = self.builder.get_object("aboutwindow")
		aboutwindow.run()
	
	""" Method to out of app """	
	def appExit(self, parameter, act = None):
		print("Exit")
		self.quit()
	
	
if __name__ == '__main__':
	app = LittleServerExecuterApp()
	app.manager = Interface(systemd, dbus_interface = 'org.freedesktop.systemd1.Manager')
	exit_status = app.run(sys.argv)
	sys.exit(exit_status)
