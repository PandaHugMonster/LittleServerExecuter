#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import gettext
import json
import locale
import os

import gi
from dbus.mainloop.glib import DBusGMainLoop

from Lse.DBus import DBus
from Lse.PageManager import PageManager
from Lse.PolkitAuth import PolkitAuth
from Lse.Systemd import Systemd
from Lse.helpers import FileAccessHelper
from Lse.models import LocalMachine
from Lse.pages import PageInfo, PageSystemd, PageHttpServer, PageDatabase, PagePHP

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gio, Gdk, Notify

DBusGMainLoop(set_as_default=True)
localedir = os.path.join(FileAccessHelper.work_directory(), 'locale')

locale.bindtextdomain("ui", localedir)
translate = gettext.translation("application", localedir)
_ = translate.gettext


class LseApp(Gtk.Application):
	""" Application Id """
	appId = "org.pandahugmonster.Lse"

	""" Version string """
	version = "0.5.0"

	pid = None
	window = None

	app_header = None
	page_manager_header = None
	_lock_button = None
	_settings = None
	_pidfile = None

	builder = None

	name = _("Little Server Executer")

	polkit_helper = None
	dbus = None

	event_granted_callbacks = []

	machine = None
	page_manager = None
	header = None

	""" Constructor """

	def __init__(self):
		super().__init__()

		self.prepare_start()

		self.prepare_interface_vars()
		self.prepare_other_libs()
		self.prepare_app_defaults()

	def prepare_start(self):
		settings_path = FileAccessHelper.get_settings_path()
		self._settings = self._get_settings(settings_path)
		self.pid = str(os.getpid())
		self._pidfile = '/tmp/pndcc.pid'

		if self._settings['pidfile']:
			self._pidfile = self._settings['pidfile']

		if FileAccessHelper.isexist(self._pidfile):
			print('Quitting')
			self.quit()
		else:
			FileAccessHelper.save(self._pidfile, self.pid)

	def _get_settings(self, settings_path:str):
		json_data = open(settings_path)
		_settings = json.load(json_data)
		json_data.close()
		return _settings

	def prepare_app_defaults(self):
		# self.machine = machine if machine else LocalMachine()
		self.machine = LocalMachine()
		self.page_manager = PageManager(self.machine, self)
		self.page_manager.set_extra_libs(dbus=self.dbus, polkit=self.polkit_helper)

	def prepare_other_libs(self):
		Gtk.Application.__init__(self, application_id=self.appId)
		Notify.init(self.pid)
		self.dbus = DBus()
		self.polkit_helper = PolkitAuth(self.dbus, self.pid)

	def prepare_interface_vars(self):
		self.header = Gtk.Box()
		self.builder = Gtk.Builder()
		self.builder.add_from_file(FileAccessHelper.get_ui("face.ui"))
		self.builder.add_from_file(FileAccessHelper.get_ui("shell.ui"))
		self.builder.set_translation_domain("ui")
		self.builder.connect_signals({"app_exit": self.app_exit})

	""" Gtk.Application Startup """

	def do_startup(self):
		Gtk.Application.do_startup(self)
		self.set_app_menu(self.builder.get_object("appmenu"))
		self.attach_actions()

	@property
	def lock_button(self):
		if not self._lock_button:
			lockbutton = Gtk.ToggleButton()
			lockbutton.set_label(_('Grant access'))
			icon_theme = Gtk.IconTheme.get_default()
			icon = Gio.ThemedIcon.new_with_default_fallbacks("changes-prevent-symbolic")
			icon_info = icon_theme.lookup_by_gicon(icon, 16, 0)
			img_lock = Gtk.Image.new_from_pixbuf(icon_info.load_icon())
			lockbutton.set_image(img_lock)
			lockbutton.set_always_show_image(True)
			lockbutton.connect("clicked", self.obtain_permission)
			self._lock_button = lockbutton

		return self._lock_button

	def prepare_headers(self):
		self.app_header = Gtk.HeaderBar()
		self.app_header.props.show_close_button = True
		self.app_header.set_custom_title(self.lock_button)

		self.page_manager_header = self.page_manager.header
		self.page_manager_header.props.show_close_button = True

		self._update_decorations(Gtk.Settings.get_default(), None)

		# self.window.hsize_group.add_widget(self.app_header)
		self.window.hsize_group.add_widget(self.app_header)
		self.window.hsize_group.add_widget(self.page_manager.side_bar)
		self.window.set_titlebar(self.header)

		self.header.add(self.app_header)
		self.header.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
		self.header.pack_start(self.page_manager_header, True, True, 0)

	def prepare_decorations(self):
		self.window = self.builder.get_object("LseWindow")
		self.window.hsize_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
		self.window.add(self.page_manager.viewpoint)
		self.add_window(self.window)
		self.load_css()

	""" Activation """

	def do_activate(self):
		self.prepare_decorations()
		self.prepare_headers()
		self.prepare_pages()

		self.change_sesitivity_of_protected_widgets(self.polkit_helper.granted)
		Gtk.Settings.get_default().connect("notify::gtk-decoration-layout", self._update_decorations)
		self.window.show_all()

	def obtain_permission(self, lockbutton):
		if lockbutton.get_active():
			managable = self.polkit_helper.grantAccess(Systemd.ACTION_MANAGE_UNITS)
		else:
			if self.polkit_helper.granted:
				self.polkit_helper.revokeAccess()
			managable = False

		icon_theme = Gtk.IconTheme.get_default()

		if not managable:
			icon = Gio.ThemedIcon.new_with_default_fallbacks("changes-prevent-symbolic")
			icon_info = icon_theme.lookup_by_gicon(icon, 16, 0)
			img_lock = Gtk.Image.new_from_pixbuf(icon_info.load_icon())
			lockbutton.set_image(img_lock)
			lockbutton.set_active(managable)
		else:
			self.app_header.set_custom_title(Gtk.Label(label=_('LSE')))
			self.app_header.show_all()

		self.change_sesitivity_of_protected_widgets(managable)

	def change_sesitivity_of_protected_widgets(self, active=False):
		for callback in self.event_granted_callbacks:
			callback(active)

	@staticmethod
	def load_css():
		css_provider = Gtk.CssProvider()
		css_provider.load_from_path(FileAccessHelper.get_ui("application.css"))
		screen = Gdk.Screen.get_default()
		context = Gtk.StyleContext()
		context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

	def attach_permission_callback(self, callback):
		self.event_granted_callbacks.append(callback)

	def prepare_pages(self):
		self.page_manager.add_page(PageInfo())
		self.page_manager.add_page(PageSystemd())
		self.page_manager.add_page(PageHttpServer())
		self.page_manager.add_page(PageDatabase())
		self.page_manager.add_page(PagePHP())

	def non_authorized(self, e):
		notification = Notify.Notification.new(self.name, _("You are not authorized to do this"), "dialog-error")
		notification.show()

	def app_about(self, action, parameter):
		about_dialog = self.builder.get_object("LseAboutDialog")
		about_dialog.set_title(_("About ") + self.name)
		about_dialog.set_program_name(self.name)
		about_dialog.set_version(self.version)
		about_dialog.run()
		about_dialog.hide()

	def app_exit(self, parameter, act=None):
		if FileAccessHelper.isexist(self._pidfile):
			FileAccessHelper.delete(self._pidfile)
		self.quit()

	def app_settings(self, parameter, act=None):
		settings_dialog = self.builder.get_object("LseSettingsDialog")
		response = settings_dialog.run()
		if response == -5:
			print("Save me [not implemented yet]")
		elif response == -6:
			print("Cancel me [not implemented yet]")
		settings_dialog.hide()

	def attach_actions(self):
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.app_about)
		self.add_action(about_action)

		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.app_exit)
		self.add_action(quit_action)

		settings_action = Gio.SimpleAction.new("settings", None)
		settings_action.connect("activate", self.app_settings)
		self.add_action(settings_action)

	# self.add_action(settingsAction)
	def _update_decorations(self, settings, pspec):
		layout_desc = settings.props.gtk_decoration_layout
		tokens = layout_desc.split(":", 1)
		print(layout_desc)
		if len(tokens) > 1:
			self.page_manager_header.props.decoration_layout = ":" + tokens[1]
		else:
			self.page_manager_header.props.decoration_layout = ""
		self.app_header.props.decoration_layout = tokens[0]
