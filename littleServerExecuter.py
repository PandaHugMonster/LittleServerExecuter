#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan@newnauka.org>
# Version: 0.4

import os
import sys
import re
import json
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from threading import Thread
from gi.repository import Gtk, Gio

from random import randint
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Notify
DBusGMainLoop(set_as_default=True)

from dbus import SystemBus, SessionBus, Interface
import gobject

currentDirectory = os.path.dirname(os.path.abspath(__file__))

bus = SystemBus()
systemd = bus.get_object('org.freedesktop.systemd1'
	, '/org/freedesktop/systemd1')

class LittleServerExecuterApp(Gtk.Application):
	""" Version string """
	version = "0.4.1"

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
	""" Gtk AboutWindow Object """
	aboutWindow = None

	""" GtkBuilder Object """
	builder = None
	
	""" Main Grid """
	grid = None
	
	""" User's UID """
	uid = None

	name = "Little Server Executer"

	""" Constructor """
	def __init__(self):
		self.pid = str(os.getpid())
		self.uid = os.getuid()
		Gtk.Application.__init__(self)
		Notify.init(self.pid)
	
	""" Gtk.Application Startup """
	def do_startup(self):
		Gtk.Application.do_startup(self)
		
		menu = Gio.Menu()
		menu.append("About", "app.about")
		menu.append("Exit", "app.quit")
		self.set_app_menu(menu)
		
		aboutAction = Gio.SimpleAction.new("about", None)
		aboutAction.connect("activate", self.appAbout)
		self.add_action(aboutAction)
		
		quitAction = Gio.SimpleAction.new("quit", None)
		quitAction.connect("activate", self.appExit)
		self.add_action(quitAction)
		
		self.manager.Subscribe()
		bus.add_signal_receiver(self.systemdJobRemoved,
                        'JobRemoved',
                        'org.freedesktop.systemd1.Manager',
                        'org.freedesktop.systemd1',
                        '/org/freedesktop/systemd1')
	
	"""	Activation """
	def do_activate(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file(currentDirectory + '/face.ui')

		self.window = self.builder.get_object("TheWindow")
		self.aboutWindow = self.builder.get_object("aboutwindow")

		self.aboutWindow.set_version(self.version)

		ab = Gtk.HeaderBar.new()
		ab.set_show_close_button(True)
		ab.set_title(self.name)

		if self.uid == 0:
			ab.set_subtitle("You are Root")
			stopAllButton = Gtk.Button.new_from_icon_name("media-playback-stop"
				, Gtk.IconSize.BUTTON)
			ab.pack_start(stopAllButton)

			startAllButton = Gtk.Button.new_from_icon_name("media-playback-start"
				, Gtk.IconSize.BUTTON)
			ab.pack_start(startAllButton)

			startAllButton.set_tooltip_text("Start all services that have"
				+ " not been started yet")
			stopAllButton.set_tooltip_text("Stop all services that have"
				+ " not been stoped yet")

			startAllButton.connect("clicked", self.startAllServicesNow)
			stopAllButton.connect("clicked", self.stopAllServicesNow)

		else:
			ab.set_subtitle("You are a regular user")
			readOnlyStatus = Gtk.Image.new_from_icon_name("emblem-readonly"
				, Gtk.IconSize.BUTTON)
			readOnlyStatus.set_tooltip_text("Read-only mode")
			ab.pack_end(readOnlyStatus)
		self.window.set_titlebar(ab)

		self.grid = self.builder.get_object("switchersGrid")
		handlers = { "appExit": self.appExit }
		self.builder.connect_signals(handlers)
			
		self.setSettings()

		self.add_window(self.window)
		self.window.show_all()


	def startAllServicesNow(self, widget):
		for (service, data) in self.services.items():
			if not data['switch'].get_active():
				data['switch'].set_active(True)

	def stopAllServicesNow(self, widget):
		for (service, data) in self.services.items():
			if data['switch'].get_active():
				data['switch'].set_active(False)

	def nonAuthorized(self):
		notification = Notify.Notification.new(self.name,
			 "You are not authorized to do this", "dialog-error")
		notification.show()

	def startService(self, service, data):
		try:
			self.manager.StartUnit(service, 'replace')
			allGood = True
		except:
			self.nonAuthorized()
			allGood = False

		return allGood

	def stopService(self, service, data):
		try:
			self.manager.StopUnit(service, 'replace')
			allGood = True
		except:
			self.nonAuthorized()
			allGood = False
			
		return allGood
		

	""" Get settings """
	def setSettings(self):
		json_data = open(currentDirectory + "/" + self.settingsFile)
		self.settings = json.load(json_data)
		json_data.close()
		self.services = {}
		for (service, title) in self.settings['services'].items():
			service_unit = self.manager.LoadUnit(service)
			service_interface = bus.get_object('org.freedesktop.systemd1'
				, str(service_unit))
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

	""" Generating the table of services from the config """
	def buildTable(self):
		prev = None
		for (service, data) in self.services.items():
			switch = data['switch']
			switch.set_active(data['state'] == 'active')
			if self.uid == 0:
				switch.connect("notify::active", self.on_switch_activated)
			else:
				switch.set_sensitive(False)
			label = Gtk.Label(data['title'])

			if not prev:
				self.grid.add(switch)
			else:
				self.grid.attach_next_to(switch, prev
					, Gtk.PositionType.BOTTOM, 1, 1)
			self.grid.attach_next_to(label, switch
				, Gtk.PositionType.RIGHT, 1, 1)
			prev = switch

	def on_switch_activated(self, switch, data):
		self.workWithService(switch)
		
		
	def workWithService(self, switch):
		for (service, data) in self.services.items():
			if data['switch'] is switch:
				prevState = switch.get_active()
				if prevState:
					self.startService(service, data)
				else:
					self.stopService(service, data)
		
	def systemdJobRemoved(self, arg1, path, service, status):
		for (servicein, data) in self.services.items():
			if servicein == service:
				if (status == 'done'):
					res = data['interface'].Get('org.freedesktop.systemd1.Unit',
						'ActiveState',
						dbus_interface='org.freedesktop.DBus.Properties')
					if (res == 'active'):
						print("Service %s is started" % service)
						data['switch'].set_state(True)
					else:
						print("Service %s is stopd" % service)
						data['switch'].set_state(False)

	""" Run App About """
	def appAbout(self, action, parameter):
		self.aboutWindow.run()

	""" Method to out of app """
	def appExit(self, parameter, act = None):
		print("Exit")
		self.quit()


if __name__ == '__main__':
	app = LittleServerExecuterApp()
	app.manager = Interface(systemd, dbus_interface = 'org.freedesktop.systemd1.Manager')
	exit_status = app.run(sys.argv)
	sys.exit(exit_status)
