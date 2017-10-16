#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4

import os

import gi
from dbus.mainloop.glib import DBusGMainLoop

from Lse.DBus import DBus
from Lse.PageManager import PageManager
from Lse.PolkitAuth import PolkitAuth
from Lse.Systemd import Systemd
from Lse.helpers import FileAccessHelper
from Lse.models import LocalMachine
from Lse.pages import PageInfo, PageSystemd

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gio, Gdk, Notify


DBusGMainLoop(set_as_default=True)


class LseApp(Gtk.Application):

    """ Application Id """
    appId = "org.pandahugmonster.Lse"

    """ Version string """
    version = "0.5.0"

    """ Application Pid Number """
    pid = None
    """ Gtk Window Object """
    window = None

    """ Left HeaderBar """
    appHB = None
    """ Right HeaderBar """
    partHB = None

    """ GtkBuilder Object """
    builder = None

    """ Main Grid """
    stack = None

    """ """
    mainView = None

    name = "Little Server Executer"
    dynbox = None
    prevPage = None

    polkit_helper = None
    dbus = None

    event_granted_callbacks = []

    machine = None
    page_manager = None
    header = None

    """ Constructor """
    def __init__(self):
        self.pid = str(os.getpid())

        super().__init__()
        self.prepare_other_libs()
        self.prepare_app_defaults()
        self.prepare_interface_vars()

    def prepare_app_defaults(self):
        # self.machine = machine if machine else LocalMachine()
        self.machine = LocalMachine()
        self.page_manager = PageManager(self.machine, self)
        self.page_manager.set_extra_libs(dbus=self.dbus, polkit=self.polkit_helper)

    def prepare_other_libs(self):
        Gtk.Application.__init__(self, application_id=self.appId)
        Notify.init(self.pid)
        Gtk.Settings.get_default().connect("notify::gtk_decoration_layout", self.update_decorations)
        self.dbus = DBus()
        self.polkit_helper = PolkitAuth(self.dbus, self.pid)

    def prepare_interface_vars(self):
        self.header = Gtk.Box()
        self.builder = Gtk.Builder()
        self.builder.add_from_file(FileAccessHelper.get_ui("face.ui"))

    """ Gtk.Application Startup """
    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.set_app_menu(self.builder.get_object("appmenu"))
        self.attach_actions()

    """ Activation """
    def do_activate(self):

        self.preapre_pages()

        self.window = self.builder.get_object("LseWindow")

        self.window.hsize_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        """ Left HeaderBar """
        self.appHB = Gtk.HeaderBar.new()
        self.appHB.props.show_close_button = True
        self.appHB.set_title(self.name)

        self.partHB = self.page_manager.header
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

        self.builder.connect_signals({"app_exit": self.app_exit})

        self.load_css()
        # self.set_settings()

        self.add_window(self.window)

        self.change_sesitivity_of_protected_widgets(self.polkit_helper.granted)

        self.window.show_all()

    def obtain_permission(self, lockbutton):

        if lockbutton.get_active():
            managable = self.polkit_helper.grantAccess(Systemd.ACTION_MANAGE_UNITS)
        else:
            if self.polkit_helper.granted:
                self.polkit_helper.revokeAccess()
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
        for callback in self.event_granted_callbacks:
            callback(active)

    @staticmethod
    def load_css():
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(FileAccessHelper.get_ui("application.css"))
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

        for page in self.page_manager.pages:
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("lse-sidebar-row")
            row.add(Gtk.Label(label=page.title))
            row.childname = page.title
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

    def attach_permission_callback(self, callback):
        self.event_granted_callbacks.append(callback)

    def preapre_pages(self):

        self.page_manager.add_page(PageInfo())
        self.page_manager.add_page(PageSystemd())

        # named = "apache"
        # page = AbstractPage(name=named, content=Gtk.Notebook.new(), title="Apache")
        #
        # scroll_view = Gtk.ScrolledWindow()
        # config_view = Gtk.TextView()
        # scroll_view.add(config_view)
        # page.content.append_page(scroll_view, Gtk.Label(label="Apache Config View"))
        # txtbuf = config_view.get_buffer()
        #
        # confpath = "/etc/httpd/conf/"
        # result = ""
        # with open(os.path.join(confpath, "httpd.conf")) as f:
        #     for line in f:
        #         result += line
        #
        # txtbuf.set_text(result)
        #
        # scroll = Gtk.ScrolledWindow()
        # colbox = Gtk.Grid()
        # colbox.set_border_width(20)
        # colbox.set_row_homogeneous(True)
        # colbox.set_row_spacing(10)
        # colbox.set_column_spacing(10)
        # scroll.add(colbox)
        # page.content.append_page(scroll, Gtk.Label(label="List of modules"))
        # # rep = page.content.get_nth_page(0)
        # # rep.pack_start(scroll)
        #
        # modpath = "/etc/httpd/modules/"
        # c = r = 0
        # for fil in list(sorted(os.listdir(modpath))):
        #     if os.path.isfile(os.path.join(modpath, fil)):
        #         colbox.attach(Gtk.Label(label=fil, xalign=0), c, r, 1, 1)
        #
        #     if (c + 1) % 3 == 0:
        #         r += 1
        #         c = 0
        #     else:
        #         c += 1
        #
        # self.pages[named] = page
        #
        # named = "mysql"
        # page = AbstractPage(name=named, content=Gtk.Notebook.new(), title="Mysql")
        #
        # scroll_view = Gtk.ScrolledWindow()
        # config_view = Gtk.TextView()
        # scroll_view.add(config_view)
        # page.content.append_page(scroll_view, Gtk.Label(label="Mysql Config View"))
        # txtbuf = config_view.get_buffer()
        #
        # confpath = "/etc/mysql/"
        # result = ""
        # with open(os.path.join(confpath, "my.cnf")) as f:
        #     for line in f:
        #         result += line
        #
        # txtbuf.set_text(result)
        # self.pages[named] = page
        #
        # named = "php"
        # page = AbstractPage(name=named, content=Gtk.Notebook.new(), title="PHP")
        # ##
        # scroll_view = Gtk.ScrolledWindow()
        # config_view = Gtk.TextView()
        # scroll_view.add(config_view)
        # page.content.append_page(scroll_view, Gtk.Label(label="PHP Config View"))
        # txtbuf = config_view.get_buffer()
        #
        # confpath = "/etc/php/"
        # result = ""
        # with open(os.path.join(confpath, "php.ini")) as f:
        #     for line in f:
        #         result += line
        #
        # txtbuf.set_text(result)
        #
        # ##
        # scroll = Gtk.ScrolledWindow()
        # colbox = Gtk.Grid()
        # colbox.set_border_width(20)
        # colbox.set_row_homogeneous(True)
        # colbox.set_row_spacing(10)
        # colbox.set_column_spacing(10)
        # scroll.add(colbox)
        # page.content.append_page(scroll, Gtk.Label(label="List of modules"))
        # modpath = "/usr/lib/php/modules/"
        # c = r = 0
        # for fil in list(sorted(os.listdir(modpath))):
        #     if os.path.isfile(os.path.join(modpath, fil)):
        #         colbox.attach(Gtk.Label(label=fil, xalign=0), c, r, 1, 1)
        #
        #     if (c + 1) % 3 == 0:
        #         r += 1
        #         c = 0
        #     else:
        #         c += 1
        #
        # self.pages[named] = page
        #
        # named = "info"
        # page = AbstractPage(name=named, content=Gtk.Notebook.new(), title="Info")
        # self.pages[named] = page

    # /usr/lib/php/modules/

    def recompose_ui(self, name):
        self.update_decorations(Gtk.Settings.get_default(), None)
        self.partHB.set_title(self.page_manager.get_page(name).title)
        self.window.queue_draw()

    def main_content(self):
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        for page in self.page_manager.pages:
            self.stack.add_named(page.content, page.title)
        return self.stack

    def non_authorized(self, e):
        notification = Notify.Notification.new(self.name, "You are not authorized to do this", "dialog-error")
        notification.show()

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
