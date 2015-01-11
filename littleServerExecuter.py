#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan@newnauka.org>
# Version: 0.3

import os
import sys
import re
import json
import time
import pyinotify
from threading import Thread
from gi.repository import Gtk
from gi.repository import Gio
from subprocess import Popen, PIPE

from random import randint

currentDirectory = os.path.dirname(os.path.abspath(__file__))

confExt = 'tuf.conf'
confDir = '/etc/nginx/servers'
defaultServerDir = '/srv/webapps'
defaultServerSubDir = ''
#
class SEventHandler(pyinotify.ProcessEvent):
	mainListenerFunction = None
	
	def process_IN_CREATE(self, event):
		if self.mainListenerFunction is not None:
			self.mainListenerFunction("on", event.pathname)
#		print("created: ", event.pathname)
		
	def process_IN_DELETE(self, event):
		if self.mainListenerFunction is not None:
			self.mainListenerFunction("off", event.pathname)
			
	def process_IIN_CLOSE_WRITE(self, event):
		if self.mainListenerFunction is not None:
			self.mainListenerFunction("offon", event.pathname)

class Watcher(Thread):

	notifier = None
	handler = None
	
	def __init__(self, hand):
		''' constructor '''
		Thread.__init__(self)
		self.handler = hand

	def run(self):
		path = '/opt/pndcc/pids/'
		wm = pyinotify.WatchManager()
		mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE
		self.notifier = pyinotify.Notifier(wm, self.handler)
		wdd = wm.add_watch(path, mask, rec=True)
		while (True):
			self.notifier.process_events()
			if self.notifier.check_events():
				self.notifier.read_events()

	def stop(self):
		self.notifier.stop()
		print("STOP")
handler = SEventHandler()
t2 = Watcher(hand=handler)
t2.daemon = True

class LSEApplication(Gtk.Application):

	pid = None
	settingsFile = "settings.json"
	pids = None
	
	builder = None
	isFlagClear = True
	rootdir = None
	subdir = None
	window = None
	text = ''
	switchersMapping = None
	settings = None
	subthread = None
	handler = None
	switch1 = None
	switch2 = None
	switch3 = None
	switch4 = None
	
	
	def __init__(self):
		self.pid = str(os.getpid())
		Gtk.Application.__init__(self)

	switched2onned = 0

	def updateState(self, etype, path):
#		if path == self.settings['services']['servers']['1']['pid']:
#			if etype == "on":
#				self.switched2onned += 1
#			else:
#				self.switched2onned -= 1
#			
#		if path == self.settings['services']['servers']['2']['pid']:
#			if etype == "on":
#				self.switched2onned += 1
#			else:
#				self.switched2onned -= 1
#				
#		if self.switched2onned == 2:
#			self.switch1.set_active(True)
#		else:
#			self.switch1.set_active(False)
		if path == self.settings['services']['nginx']['1']['pid']:
			if etype == "on":
				self.switch1.set_active(True)
			else:
				self.switch1.set_active(False)

			
		if path == self.settings['services']['httpd']['1']['pid']:
			if etype == "on":
				self.switch2.set_active(True)
			else:
				self.switch2.set_active(False)
				
		if path == self.settings['services']['postgres']['1']['pid']:
			if etype == "on":
				self.switch3.set_active(True)
			else:
				self.switch3.set_active(False)
				
		if path == self.settings['services']['mysqld']['1']['pid']:
			if etype == "on":
				self.switch4.set_active(True)
			else:
				self.switch4.set_active(False)
			

	def do_activate(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file(currentDirectory + '/face.ui')
		
		self.handler.mainListenerFunction = self.updateState
		self.window = self.builder.get_object("TheWindow")
		handlers = {
			"on_switch_activate": self.on_switch_activate,
			"onDnbaseNameChanged": self.onDnbaseNameChanged,
			"appExit": self.appExit,
			"runReplacement": self.runReplacement
		}
		self.builder.connect_signals(handlers)
		
		self.rootdir = self.builder.get_object("rootdir")
		self.subdir = self.builder.get_object("subdir")
		
		self.rootdir.set_text(defaultServerDir)
		self.subdir.set_text(defaultServerSubDir)

		self.switchersMapping = {
			"switch1": "status1",
			"switch2": "status2",
			"switch3": "status3",
			"switch4": "status4",
		}
		
		self.switch1 = self.builder.get_object("switch1")
		self.switch2 = self.builder.get_object("switch2")
		self.switch3 = self.builder.get_object("switch3")
		self.switch4 = self.builder.get_object("switch4")
		
		self.fillTheHostsList()
		self.setSettings()
		
		data0 = data1 = data2 = data3 = data4 = True
		
		if int(self.pids["nginx"][0]) < 0:
			data0 = False
		if int(self.pids["nginx"][1]) < 0:
			data1 = False
		self.switch1.set_active(data0 and data1)


		if int(self.pids["httpd"]) < 0:
			data2 = False
		self.switch2.set_active(data2)

		if int(self.pids["postgres"]) < 0:
			data3 = False
		self.switch3.set_active(data3)
		
		if int(self.pids["mysqld"]) < 0:
			data4 = False
		self.switch4.set_active(data4)
	
		self.add_window(self.window)
		self.window.show_all()

	def setSettings(self):
		json_data = open(currentDirectory + "/" + self.settingsFile)
		self.settings = json.load(json_data)
		json_data.close()
		
		self.updatePidsInfo()
		
		
	def updatePidsInfo(self):
		
		pid1 = pid2 = pid3 = pid4 = pid5 = None
		if os.path.isfile(self.settings['services']['nginx']['1']['pid']):
			f = open(self.settings['services']['nginx']['1']['pid'])
			pid1 = int(f.read())
			f.close()
		else:
			pid1 = -1
		
		if os.path.isfile(self.settings['services']['nginx']['2']['pid']):
			f = open(self.settings['services']['nginx']['2']['pid'])
			pid2 = int(f.read())
			f.close()
		else:
			pid2 = -1
		
		if os.path.isfile(self.settings['services']['httpd']['1']['pid']):
			f = open(self.settings['services']['httpd']['1']['pid'])
			pid3 = int(f.read())
			f.close()
		else:
			pid3 = -1
			
		if os.path.isfile(self.settings['services']['postgres']['1']['pid']):
			f = open(self.settings['services']['postgres']['1']['pid'])
			pid4 = int(f.read())
			f.close()
		else:
			pid4 = -1
			
		if os.path.isfile(self.settings['services']['mysqld']['1']['pid']):
			f = open(self.settings['services']['mysqld']['1']['pid'])
			pid5 = int(f.read())
			f.close()
		else:
			pid5 = -1
		
		print(str(pid1) + ' ' + str(pid2) + ' ' + str(pid3) + ' ' + str(pid4) + ' ' + str(pid5))
		self.pids = {
			"nginx": (pid1,pid2),
			"httpd": pid3,
			"postgres": pid4,
			"mysqld": pid5
		}

	def fillTheHostsList(self):
		listbox = self.builder.get_object("listbox1")
		
		f = open('/etc/hosts', encoding='utf-8')
		ln = 0

		for line in f.readlines():
			ln += 1
			if re.search('127\.0\.0\.1', line):
				print(line, end = '')
				words = line.split()
				for item in words:
					if not re.match('127\.0\.0\.1', item):
						label = Gtk.LinkButton('http://' + item, item)
						label.set_vexpand(True)
						label.set_halign(Gtk.Align.START)
						listbox.add(label)
		f.close()

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
		
	set_locker = False
		

	def appAbout(self, action, parameter):
		aboutwindow = self.builder.get_object("aboutwindow")
		aboutwindow.run()
		
	def on_switch_activate(self, switch, ttype):
		name = Gtk.Buildable.get_name(switch)
		status = self.builder.get_object(self.switchersMapping[name])
	
		if not self.set_locker:
			if name == "switch1":
				self.set_locker = True
				self.switchon1(switch.get_active(), status)
				self.set_locker = False
			elif name == "switch2":
				self.set_locker = True
				self.switchon2(switch.get_active(), status)
				self.set_locker = False
			elif name == "switch3":
				self.set_locker = True
				self.switchon3(switch.get_active(), status)
				self.set_locker = False
			elif name == "switch4":
				self.set_locker = True
				self.switchon4(switch.get_active(), status)
				self.set_locker = False
	
	def switchon1(self, boo, status):
		if boo:
			Popen([
				self.settings['app']['systemcontrol'], 
				"start", 
				self.settings['services']['nginx']['1']['name'], 
				self.settings['services']['nginx']['2']['name']
			])
			status.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
		else:
			Popen([
				self.settings['app']['systemcontrol'], 
				"stop", 
				self.settings['services']['nginx']['1']['name'], 
				self.settings['services']['nginx']['2']['name']
			])
			status.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)

	def switchon2(self, boo, status):
		if boo:
			Popen([
				self.settings['app']['systemcontrol'], 
				"start", 
				self.settings['services']['httpd']['1']['name']
			])
			status.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
		else:
			Popen([
				self.settings['app']['systemcontrol'], 
				"stop", 
				self.settings['services']['httpd']['1']['name']
			])
			status.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
	
	def switchon3(self, boo, status):
		if boo:
			Popen([
				self.settings['app']['systemcontrol'], 
				"start", 
				self.settings['services']['postgres']['1']['name']
			])
			status.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
		else:
			Popen([
				self.settings['app']['systemcontrol'], 
				"stop", 
				self.settings['services']['postgres']['1']['name']
			])
			status.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
			
	def switchon4(self, boo, status):
		if boo:
			Popen([
				self.settings['app']['systemcontrol'], 
				"start", 
				self.settings['services']['mysqld']['1']['name']
			])
			status.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
		else:
			Popen([
				self.settings['app']['systemcontrol'], 
				"stop", 
				self.settings['services']['mysqld']['1']['name']
			])
			status.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
		
		
	def appExit(self, parameter):
		print("REST")
		self.quit()

	def runReplacement(self, button):
		f = open(currentDirectory + '/files/yii_common_server.template', 'r')
		self.text = f.read()
		f.close()
		
		dnbase_name = self.builder.get_object("dnbase_name")
		subdomain = self.builder.get_object("subdomain")
	
		wordMapping = [
			['dnbase_name', dnbase_name.get_text()], 
			['subdomain', subdomain.get_text()], 
			['rootdir', self.rootdir.get_text()], 
			['subdir', self.subdir.get_text()]
		]
		self.replaceAllNeeded(wordMapping)
		self.printText()
	
	def onDnbaseNameChanged(self, entry):
		fielddata = entry.get_text()
		preName = self.builder.get_object("pre_name")
		subdomain = self.builder.get_object("subdomain")
		if self.isFlagClear:
			subdomain.set_text(fielddata)
		preName.set_markup("<b>" + self.fileOutName(fielddata) + "</b>")

	def replaceAllNeeded(self, wordMapping):
		for finwor, replac in wordMapping:
			self.text = self.text.replace('__REPLACE__' + finwor, replac)
	
	def fileOutName(self, name):
		return confDir + '/' + name + '.' + confExt
	
	def printText(self):
		for t in self.text:
			print(t, end='')
		

if __name__ == '__main__':
	t2.start()
	app = LSEApplication()
	app.subthread = t2
	app.handler = handler
	exit_status = app.run(sys.argv)
	sys.exit(exit_status)
	
