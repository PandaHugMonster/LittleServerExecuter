#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

import os
import sys
import re
import json
import time

import LSEPage

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from threading import Thread
from gi.repository import Gtk, Gio, Gdk, GObject, GdkPixbuf

from random import randint
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Notify
DBusGMainLoop(set_as_default = True)

from dbus import SystemBus, SessionBus, Interface
import gobject

currentDirectory = os.path.dirname(os.path.abspath(__file__))

bus = SystemBus()
systemd = bus.get_object('org.freedesktop.systemd1'
	, '/org/freedesktop/systemd1')

class LittleServerExecuterApp(Gtk.Application):
	""" Application Id """
	appId = "org.pandahugmonster.lse"

	""" Version string """
	version = "0.4.2"

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

	""" Left HeaderBar """
	appHB = None
	""" Right HeaderBar """
	partHB = None

	""" GtkBuilder Object """
	builder = None
	
	""" Main Grid """
	grid = None
	stack = None

	""" """
	mainView = None

	""" User's UID """
	uid = None

	name = "Little Server Executer"
	dynbox = None
	prevPage = None

	""" Constructor """
	def __init__(self):
		self.pid = str(os.getpid())
		self.uid = os.getuid()
		Gtk.Application.__init__(self, application_id = self.appId)
		Notify.init(self.pid)

		Gtk.Settings.get_default().connect("notify::gtk_decoration_layout"
			, self.updateDecorations)



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
		
		"""settingsAction = Gio.SimpleAction.new("settings", None)
		settingsAction.connect("activate", self.appSettings)
		self.add_action(quitAction)"""

		self.manager.Subscribe()
		bus.add_signal_receiver(self.systemdJobRemoved,
			'JobRemoved',
			'org.freedesktop.systemd1.Manager',
			'org.freedesktop.systemd1',
			'/org/freedesktop/systemd1')
	
	"""	Activation """
	def do_activate(self):
		self.preaprePages()
		self.builder = Gtk.Builder()
		self.builder.add_from_file(os.path.join(currentDirectory, 'face.ui'))

		self.window = self.builder.get_object("LseWindow")
		self.window.hsize_group = Gtk.SizeGroup(mode = Gtk.SizeGroupMode.HORIZONTAL)
		self.header = Gtk.Box()

		""" Left HeaderBar """
		self.appHB = Gtk.HeaderBar.new()
		self.appHB.props.show_close_button = True
		self.appHB.set_title(self.name)
		self.partHB = Gtk.HeaderBar()
		self.partHB.props.show_close_button = True

		self.mainView = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)

		self.recomposeUI("systemd")
		sidebar = self.sideBar()
		viewpoint = self.mainContent()

		self.mainView.pack_start(sidebar, False, False, 0)
		self.mainView.pack_start(Gtk.Separator(orientation = Gtk.Orientation.VERTICAL)
			, False, False, 0)
		self.mainView.pack_start(viewpoint, True, True, 0)

		self.window.add(self.mainView)

		if self.uid == 0:
			self.appHB.set_subtitle("You are Root")
		else:
			self.appHB.set_subtitle("You are a regular user")
			readOnlyStatus = Gtk.Image.new_from_icon_name("emblem-readonly"
				, Gtk.IconSize.BUTTON)
			readOnlyStatus.set_tooltip_text("Read-only mode")
			self.appHB.pack_end(readOnlyStatus)

		self.header.add(self.appHB)
		self.header.add(Gtk.Separator(orientation = Gtk.Orientation.VERTICAL))
		self.header.pack_start(self.partHB, True, True, 0)

		self.window.hsize_group.add_widget(self.appHB)
		self.window.set_titlebar(self.header)

		handlers = { "appExit": self.appExit }
		self.builder.connect_signals(handlers)

		self.loadCss()

		self.setSettings()

		self.add_window(self.window)
		self.window.show_all()

	def loadCss(self):
		cssProvider = Gtk.CssProvider()
		cssProvider.load_from_path(os.path.join(currentDirectory, "application.css"))
		screen = Gdk.Screen.get_default()
		context = Gtk.StyleContext()
		context.add_provider_for_screen(screen, cssProvider
			, Gtk.STYLE_PROVIDER_PRIORITY_USER)

	def sideBar(self):
		box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		listbox = Gtk.ListBox()
		listbox.get_style_context().add_class("lse-sidebar")
		listbox.set_size_request(250, -1)
		listbox.connect("row-selected", self.changeViewpoint)
		listbox.set_header_func(self.listHeaderFunc, None)
		scroll = Gtk.ScrolledWindow()
		scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		scroll.add(listbox)
		box.pack_start(scroll, True, True, 0)
		self.window.hsize_group.add_widget(box)

		keys = list(reversed(sorted(self.pages.keys())))
		for name in keys:
			page = self.pages[name]
			row = Gtk.ListBoxRow()
			row.get_style_context().add_class("lse-sidebar-row")
			row.add(Gtk.Label(label = page.title))
			row.childname = name
			listbox.add(row)

		return box

	def listHeaderFunc(self, row, before, user_data):
		if before and not row.get_header():
			row.set_header(
				Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL))

	def changeViewpoint(self, list, row):
		if isinstance(row, Gtk.ListBoxRow):
			self.stack.set_visible_child_name(row.childname)
			self.recomposeUI(row.childname)

	def preaprePages(self):
		self.pages = {}

		named = "systemd"
		self.grid = Gtk.Grid()
		self.grid.set_border_width(10)
		page = LSEPage.LSEPage(name = named, content = self.grid, title = "SystemD Control")
		self.pages[named] = page

		named = "apache"
		page = LSEPage.LSEPage(name = named, content = Gtk.Label(label = "Apache"), title = "Apache")
		self.pages[named] = page

		named = "mysql"
		page = LSEPage.LSEPage(name = named, content = Gtk.Label(label = "Mysql"), title = "Mysql")
		self.pages[named] = page

	def recomposeUI(self, name):
		self.updateDecorations(Gtk.Settings.get_default(), None)

		self.partHB.set_title(self.pages[name].title)

		self.window.queue_draw()

	def mainContent(self):
		self.stack = Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

		keys = list(reversed(sorted(self.pages.keys())))
		for name in keys:
			page = self.pages[name]
			self.stack.add_named(page.content, name)
		return self.stack

	def processGroupServicesNow(self, action, groupName):
		for (group, gdata) in self.services.items():
			if group == groupName:
				for (service, data) in gdata.items():
					if data['switch'].get_active() != action:
						data['switch'].set_active(action)

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
		json_data = open(os.path.join(currentDirectory, self.settingsFile))
		self.settings = json.load(json_data)
		json_data.close()
		self.services = {}
		for (group, datag) in self.settings['services'].items():
			self.services[group] = {}
			for (service, title) in datag.items():
				service_unit = self.manager.LoadUnit(service)
				service_interface = bus.get_object('org.freedesktop.systemd1'
					, str(service_unit))
				state = service_interface.Get('org.freedesktop.systemd1.Unit',
					'ActiveState',
					dbus_interface='org.freedesktop.DBus.Properties')
				self.services[group][service] = {
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
		self.grid.set_row_spacing(15)
		self.grid.set_column_spacing(20)
		self.grid.get_style_context().add_class("lse-grid")
		prev = None
		keys = list(sorted(self.services.keys()))
		for group in keys:
			datag = self.services[group]

			groupName = Gtk.Label(label = group)
			box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)

			if self.uid == 0:
				stopAllButton = Gtk.Button.new_from_icon_name("media-playback-stop"
					, Gtk.IconSize.BUTTON)
				startAllButton = Gtk.Button.new_from_icon_name("media-playback-start"
					, Gtk.IconSize.BUTTON)
				startAllButton.group = group
				stopAllButton.group = group

				startAllButton.connect("clicked", lambda widget: self.processGroupServicesNow(True, widget.group))
				stopAllButton.connect("clicked", lambda widget: self.processGroupServicesNow(False, widget.group))

				box.add(startAllButton)
				box.add(stopAllButton)

			if not prev:
				self.grid.add(groupName)
			else:
				self.grid.attach_next_to(groupName, prev
					, Gtk.PositionType.BOTTOM, 1, 1)
			self.grid.attach_next_to(box, groupName
					, Gtk.PositionType.RIGHT, 1, 1)
			prepre = None
			for (service, data) in datag.items():
				switch = data['switch']
				switch.set_active(data['state'] == 'active')
				if self.uid == 0:
					switch.connect("notify::active", self.on_switch_activated)
				else:
					switch.set_sensitive(False)
				label = Gtk.Label(label = data['title'], xalign = 0)

				if not prepre:
					prepre = True
					self.grid.attach_next_to(switch, groupName
						, Gtk.PositionType.BOTTOM, 1, 1)
				else:
					self.grid.attach_next_to(switch, prev
						, Gtk.PositionType.BOTTOM, 1, 1)
				self.grid.attach_next_to(label, switch
					, Gtk.PositionType.RIGHT, 1, 1)
				prev = switch

	def on_switch_activated(self, switch, data):
		self.workWithService(switch)


	def workWithService(self, switch):
		for (group, datag) in self.services.items():
			for (service, data) in datag.items():
				if data['switch'] is switch:
					prevState = switch.get_active()
					if prevState:
						self.startService(service, data)
					else:
						self.stopService(service, data)

	def systemdJobRemoved(self, arg1, path, service, status):
		for (group, datag) in self.services.items():
			for (servicein, data) in datag.items():
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

	def updateDecorations(self, settings, pspec):
		layout_desc = settings.props.gtk_decoration_layout
		tokens = layout_desc.split(":", 2)
		if tokens != None:
			self.partHB.props.decoration_layout = ":" + tokens[1]
			self.appHB.props.decoration_layout = tokens[0]



	""" Run App About """
	def appAbout(self, action, parameter):
		""" Gtk AboutWindow Object """
		aboutDialog = Gtk.AboutDialog()
		aboutDialog.set_transient_for(self.window)
		aboutDialog.set_title("About " + self.name)
		aboutDialog.set_program_name(self.name)
		aboutDialog.set_comments(
			'The simplest Python + Gtk application to control '
			+ 'Systemd services such as httpd, mariadb and so on. '
			+ 'A part of the "Panda\'s Control Centre"')
		aboutDialog.set_version(self.version)
		aboutDialog.set_copyright("Copyright \xa9 2015 Ivan Ponomarev.")
		aboutDialog.set_website("https://github.com/PandaHugMonster/LittleServerExecuter")
		aboutDialog.set_website_label("github.com/PandaHugMonster/LittleServerExecuter")
		aboutDialog.set_license_type(Gtk.License.GPL_2_0)
		authors = [
		    "Panda Hug Monster <ivan.guineapig@gmail.com>"
		]
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(currentDirectory
			, 'drawing_LSE_logo.png'))
		aboutDialog.set_logo(pixbuf)
		aboutDialog.set_authors(authors)
		aboutDialog.connect("response", lambda w, r: aboutDialog.destroy())
		aboutDialog.show()

	def appExit(self, parameter, act = None):
		print("Exit")
		self.quit()



if __name__ == '__main__':
	app = LittleServerExecuterApp()
	app.manager = Interface(systemd, dbus_interface = 'org.freedesktop.systemd1.Manager')
	exit_status = app.run(sys.argv)
	sys.exit(exit_status)
