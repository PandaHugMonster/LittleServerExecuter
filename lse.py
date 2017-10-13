#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

import datetime
import json
import os
import sys

import gi
from dbus.mainloop.glib import DBusGMainLoop

from Lse import DBus, Page, Systemd, PolkitAuth

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gio, Gdk, Notify

from pathlib import Path

DBusGMainLoop(set_as_default=True)

currentDirectory = os.path.dirname(os.path.abspath(__file__))


class LittleServerExecuterApp(Gtk.Application):

    """ Application Id """
    appId = "org.pandahugmonster.Lse"

    """ Version string """
    version = "0.4.4"

    """ Settings file """
    settingsFile = "settings.json"

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

    name = "Little Server Executer"
    dynbox = None
    prevPage = None

    polkitHelper = None
    protectedWidgets = []

    switchesServiceLock = False

    """ Constructor """

    def __init__(self):
        self.pid = str(os.getpid())
        Gtk.Application.__init__(self, application_id=self.appId)
        Notify.init(self.pid)

        Gtk.Settings.get_default().connect("notify::gtk_decoration_layout", self.update_decorations)

        self.dbus = DBus()
        self.polkitHelper = PolkitAuth(self.dbus, self.pid)
        self.systemd = Systemd(self.dbus, self.polkitHelper)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(currentDirectory, 'ui/face.ui'))

        self.header = Gtk.Box()
        self.pages = {}
        self.services = {}

    """ Gtk.Application Startup """
    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.set_app_menu(self.builder.get_object("appmenu"))

        self.attach_actions()

        self.systemd.signalReceiver(self.systemd_job_removed)

    """ Activation """
    def do_activate(self):
        self.preapre_pages()

        self.window = self.builder.get_object("LseWindow")

        self.window.hsize_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        """ Left HeaderBar """
        self.appHB = Gtk.HeaderBar.new()
        self.appHB.props.show_close_button = True
        self.appHB.set_title(self.name)
        self.partHB = Gtk.HeaderBar()
        self.partHB.props.show_close_button = True

        self.mainView = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # self.recompose_ui("systemd")
        sidebar = self.side_bar()
        viewpoint = self.main_content()

        self.mainView.pack_start(sidebar, False, False, 0)
        self.mainView.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        self.mainView.pack_start(viewpoint, True, True, 0)

        self.window.add(self.mainView)

        lockbutton = Gtk.ToggleButton(label="Locked")

        icon_theme = Gtk.IconTheme.get_default()
        icon = Gio.ThemedIcon.new_with_default_fallbacks("changes-prevent-symbolic")
        icon_info = icon_theme.lookup_by_gicon(icon, 16, 0)
        img_lock = Gtk.Image.new_from_pixbuf(icon_info.load_icon())

        lockbutton.set_image(img_lock)
        lockbutton.set_always_show_image(True)

        lockbutton.connect("clicked", self.obtain_permission)
        self.partHB.pack_end(lockbutton)

        self.header.add(self.appHB)
        self.header.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.header.pack_start(self.partHB, True, True, 0)

        self.window.hsize_group.add_widget(self.appHB)
        self.window.set_titlebar(self.header)

        handlers = {"app_exit": self.app_exit}
        self.builder.connect_signals(handlers)

        self.load_css()
        self.set_settings()

        self.add_window(self.window)

        self.change_sesitivity_of_protected_widgets(self.polkitHelper.granted)

        self.window.show_all()

    def obtain_permission(self, lockbutton):

        if lockbutton.get_active():
            managable = self.polkitHelper.grantAccess(Systemd.ACTION_MANAGE_UNITS)
        else:
            if self.polkitHelper.granted:
                self.polkitHelper.revokeAccess()
            managable = False

        icon_theme = Gtk.IconTheme.get_default()

        if managable:
            sub_name = 'Unlocked'
            icon = Gio.ThemedIcon.new_with_default_fallbacks("changes-allow-symbolic")
        else:
            sub_name = 'Locked'
            icon = Gio.ThemedIcon.new_with_default_fallbacks("changes-prevent-symbolic")

        icon_info = icon_theme.lookup_by_gicon(icon, 16, 0)
        img_lock = Gtk.Image.new_from_pixbuf(icon_info.load_icon())

        lockbutton.set_image(img_lock)

        lockbutton.set_label(sub_name)
        lockbutton.set_active(managable)

        self.change_sesitivity_of_protected_widgets(managable)

    def change_sesitivity_of_protected_widgets(self, active=False):
        for widget in self.protectedWidgets:
            widget.set_sensitive(active)

    @staticmethod
    def load_css():
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.join(currentDirectory, "ui/application.css"))
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def side_bar(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        listbox = Gtk.ListBox()
        listbox.get_style_context().add_class("lse-sidebar")
        listbox.set_size_request(250, -1)
        listbox.connect("row-selected", self.change_viewpoint)
        listbox.set_header_func(self.list_header_func, None)
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
            row.add(Gtk.Label(label=page.title))
            row.childname = name
            listbox.add(row)

        return box

    @staticmethod
    def list_header_func(row, before, user_data):
        if before and not row.get_header():
            row.set_header(
                Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def change_viewpoint(self, list, row):
        if isinstance(row, Gtk.ListBoxRow):
            self.stack.set_visible_child_name(row.childname)
            self.recompose_ui(row.childname)

    def preapre_pages(self):
        named = "systemd"
        self.grid = Gtk.Grid()
        self.grid.set_border_width(20)
        sw = Gtk.ScrolledWindow()
        sw.add(self.grid)
        page = Page(name=named, content=sw, title="SystemD Control")
        self.pages[named] = page

        named = "apache"
        page = Page(name=named, content=Gtk.Notebook.new(), title="Apache")

        scroll_view = Gtk.ScrolledWindow()
        config_view = Gtk.TextView()
        scroll_view.add(config_view)
        page.content.append_page(scroll_view, Gtk.Label(label="Apache Config View"))
        txtbuf = config_view.get_buffer()

        confpath = "/etc/httpd/conf/"
        result = ""
        with open(os.path.join(confpath, "httpd.conf")) as f:
            for line in f:
                result += line

        txtbuf.set_text(result)

        scroll = Gtk.ScrolledWindow()
        colbox = Gtk.Grid()
        colbox.set_border_width(20)
        colbox.set_row_homogeneous(True)
        colbox.set_row_spacing(10)
        colbox.set_column_spacing(10)
        scroll.add(colbox)
        page.content.append_page(scroll, Gtk.Label(label="List of modules"))
        # rep = page.content.get_nth_page(0)
        # rep.pack_start(scroll)

        modpath = "/etc/httpd/modules/"
        c = r = 0
        for fil in list(sorted(os.listdir(modpath))):
            if os.path.isfile(os.path.join(modpath, fil)):
                colbox.attach(Gtk.Label(label=fil, xalign=0), c, r, 1, 1)

            if (c + 1) % 3 == 0:
                r += 1
                c = 0
            else:
                c += 1

        self.pages[named] = page

        named = "mysql"
        page = Page(name=named, content=Gtk.Notebook.new(), title="Mysql")

        scroll_view = Gtk.ScrolledWindow()
        config_view = Gtk.TextView()
        scroll_view.add(config_view)
        page.content.append_page(scroll_view, Gtk.Label(label="Mysql Config View"))
        txtbuf = config_view.get_buffer()

        confpath = "/etc/mysql/"
        result = ""
        with open(os.path.join(confpath, "my.cnf")) as f:
            for line in f:
                result += line

        txtbuf.set_text(result)
        self.pages[named] = page

        named = "php"
        page = Page(name=named, content=Gtk.Notebook.new(), title="PHP")
        ##
        scroll_view = Gtk.ScrolledWindow()
        config_view = Gtk.TextView()
        scroll_view.add(config_view)
        page.content.append_page(scroll_view, Gtk.Label(label="PHP Config View"))
        txtbuf = config_view.get_buffer()

        confpath = "/etc/php/"
        result = ""
        with open(os.path.join(confpath, "php.ini")) as f:
            for line in f:
                result += line

        txtbuf.set_text(result)

        ##
        scroll = Gtk.ScrolledWindow()
        colbox = Gtk.Grid()
        colbox.set_border_width(20)
        colbox.set_row_homogeneous(True)
        colbox.set_row_spacing(10)
        colbox.set_column_spacing(10)
        scroll.add(colbox)
        page.content.append_page(scroll, Gtk.Label(label="List of modules"))
        modpath = "/usr/lib/php/modules/"
        c = r = 0
        for fil in list(sorted(os.listdir(modpath))):
            if os.path.isfile(os.path.join(modpath, fil)):
                colbox.attach(Gtk.Label(label=fil, xalign=0), c, r, 1, 1)

            if (c + 1) % 3 == 0:
                r += 1
                c = 0
            else:
                c += 1

        self.pages[named] = page

    # /usr/lib/php/modules/

    def recompose_ui(self, name):
        self.update_decorations(Gtk.Settings.get_default(), None)

        self.partHB.set_title(self.pages[name].title)

        self.window.queue_draw()

    def main_content(self):
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

        keys = list(reversed(sorted(self.pages.keys())))
        for name in keys:
            page = self.pages[name]
            self.stack.add_named(page.content, name)
        return self.stack

    def process_group_services_now(self, action, group_name):
        for (group, gdata) in self.services.items():
            if group == group_name:
                for (service, data) in gdata.items():
                    if data['switch'].get_active() != action:
                        data['switch'].set_active(action)

    def non_authorized(self, e):
        notification = Notify.Notification.new(self.name, "You are not authorized to do this", "dialog-error")
        notification.show()

    """ Get settings """

    def get_settings_data(self):
        sub_path = os.path.join(Path.home(), ".lse/" + self.settingsFile)

        if not os.path.isfile(sub_path):
            sub_path = os.path.join(currentDirectory, "/etc/lse/" + self.settingsFile)
            if not os.path.isfile(sub_path):
                sub_path = os.path.join(currentDirectory, "extras/" + self.settingsFile)

        print("Settings loaded from: " + sub_path)

        json_data = open(sub_path)
        settings = json.load(json_data)
        json_data.close()
        return settings

    def set_settings(self):
        self.settings = self.get_settings_data()

        for (group, datag) in self.settings['services'].items():
            self.services[group] = {}
            for (service, title) in datag.items():
                service_unit = self.systemd.loadUnit(service)
                service_interface = self.dbus.getObject('org.freedesktop.systemd1', str(service_unit))
                state = service_interface.Get('org.freedesktop.systemd1.Unit', 'ActiveState',
                                              dbus_interface='org.freedesktop.DBus.Properties')
                self.services[group][service] = {
                    'unit': service_unit,
                    'interface': service_interface,
                    'title': title,
                    'state': state,
                    'switch': Gtk.Switch(),
                    'spinner': Gtk.Spinner(),
                }
            # print("%s = %s | %s" % (service, title, state))

        self.build_table()

    """ Generating the table of services from the config """

    def build_table(self):
        self.grid.set_row_spacing(15)
        self.grid.set_column_spacing(20)
        self.grid.get_style_context().add_class("lse-grid")
        prev = None
        keys = list(sorted(self.services.keys()))
        for group in keys:
            datag = self.services[group]

            group_name = Gtk.Label(label=group)
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            # if self.uid == 0:
            stop_all_button = Gtk.Button.new_from_icon_name("media-playback-stop", Gtk.IconSize.BUTTON)
            start_all_button = Gtk.Button.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
            start_all_button.group = group
            stop_all_button.group = group

            start_all_button.connect("clicked", lambda widget: self.process_group_services_now(True, widget.group))
            stop_all_button.connect("clicked", lambda widget: self.process_group_services_now(False, widget.group))

            self.protectedWidgets.append(start_all_button)
            self.protectedWidgets.append(stop_all_button)

            box.add(start_all_button)
            box.add(stop_all_button)

            if not prev:
                self.grid.add(group_name)
            else:
                self.grid.attach_next_to(group_name, prev, Gtk.PositionType.BOTTOM, 1, 1)
            self.grid.attach_next_to(box, group_name, Gtk.PositionType.RIGHT, 1, 1)
            prepre = None
            for (service, data) in datag.items():
                switch = data['switch']
                spinner = data['spinner']
                switch.set_active(data['state'] == 'active')
                switch.connect("notify::active", self.work_with_service)
                self.protectedWidgets.append(switch)
                label = Gtk.Label(label=data['title'], xalign=0)

                if not prepre:
                    prepre = True
                    self.grid.attach_next_to(switch, group_name, Gtk.PositionType.BOTTOM, 1, 1)
                else:
                    self.grid.attach_next_to(switch, prev, Gtk.PositionType.BOTTOM, 1, 1)
                self.grid.attach_next_to(label, switch, Gtk.PositionType.RIGHT, 1, 1)
                self.grid.attach_next_to(spinner, label, Gtk.PositionType.RIGHT, 1, 1)
                prev = switch

    def work_with_service(self, switch, data):
        if not self.switchesServiceLock:
            for (group, datag) in self.services.items():
                for (service, data) in datag.items():
                    if data['switch'] is switch:
                        data["spinner"].start()
                        data['lastactiontime'] = datetime.datetime.now()
                        last = data["lastactiontime"]

                        prev_state = switch.get_active()
                        if prev_state:
                            print("Systemd Start executed [%s]" % service)
                            self.systemd.startService(service)
                        else:
                            print("Systemd Stop executed [%s]" % service)
                            self.systemd.stopService(service)

    def preserved_switch(self, switcher, state):
        self.switchesServiceLock = True
        switcher.set_state(state)
        self.switchesServiceLock = False

    def systemd_job_removed(self, arg1, path, service, status):
        for (group, datag) in self.services.items():
            for (servicein, data) in datag.items():
                spinner = data["spinner"]
                if servicein == service:
                    if status == 'done':
                        spinner.stop()
                        res = data['interface'].Get('org.freedesktop.systemd1.Unit', 'ActiveState',
                                                    dbus_interface='org.freedesktop.DBus.Properties')
                        if res == 'active':
                            self.preserved_switch(data['switch'], True)
                        else:
                            self.preserved_switch(data['switch'], False)

    def update_decorations(self, settings, pspec):
        layout_desc = settings.props.gtk_decoration_layout
        tokens = layout_desc.split(":", 2)
        if tokens is not None:
            self.partHB.props.decoration_layout = ":" + tokens[1]
            self.appHB.props.decoration_layout = tokens[0]

    """ Run App About """

    def app_about(self, action, parameter):
        """ Gtk AboutWindow Object """
        about_dialog = self.builder.get_object("LseAboutDialog")
        about_dialog.set_title("About " + self.name)
        about_dialog.set_program_name(self.name)
        about_dialog.set_version(self.version)
        about_dialog.run()
        about_dialog.hide()

    def app_exit(self, parameter, act=None):
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

    # self.add_action(settingsAction)


if __name__ == '__main__':
    app = LittleServerExecuterApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
