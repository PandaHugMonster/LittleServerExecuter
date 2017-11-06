#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import datetime
import gettext
import os

from dbus.exceptions import DBusException
from gi.repository import Gtk

from Lse.AbstractPage import AbstractPage
from Lse.PageManager import PageManager
from Lse.Systemd import Systemd
from Lse.helpers import FileAccessHelper

localedir = os.path.join(FileAccessHelper.work_directory(), 'locale')
translate = gettext.translation("pages", localedir)
_ = translate.gettext


class PageSystemd(AbstractPage):

    grid = None
    notebook = None
    _is_permission_needed = True
    protected_widgets = []
    systemd = None
    _services_completed = None
    all_services = []

    def __init__(self):
        name = "page_systemd"
        title = _("SystemD Control")
        super().__init__(name, title)

    def attach_init(self, page_manager:PageManager):
        super().attach_init(page_manager)
        self.systemd = Systemd(page_manager.dbus, page_manager.polkit_helper)
        self.systemd.signalReceiver(self.systemd_job_removed)

    def permission_granted_callback(self, status: bool):
        for widget in self.protected_widgets:
            widget.set_sensitive(status)

    @property
    def get_main_container(self) -> Gtk.Box:
        if not self.notebook:
            self.notebook = Gtk.Notebook.new()
        return self.notebook

    def groups_show(self):
        self.grid = Gtk.Grid()
        sw = Gtk.ScrolledWindow()
        sw.add(self.grid)

        self.grid.set_border_width(20)
        self.grid.set_row_spacing(15)
        self.grid.set_column_spacing(20)
        self.grid.get_style_context().add_class("lse-grid")
        # builder.get_object("place_kernel").set_text(machine.version)
        self.build_table()
        return sw

    def all_services_list(self):
        listy = self.systemd.listUnits()
        res = {}

        for item in listy:
            sub = self.systemd.get_service_common_info(item)
            res[sub['Id']] = sub['Description'] + " [ %s ]" % sub['Id']

        return {'All Services': res}

    def all_services_show(self):
        rawservices = self.all_services_list()

        grid = Gtk.Grid()
        sw = Gtk.ScrolledWindow()
        sw.add(grid)

        grid.set_border_width(20)
        grid.set_row_spacing(15)
        grid.set_column_spacing(20)
        grid.get_style_context().add_class("lse-grid")

        self.all_services = self.prepare_services(rawservices)
        self.build_table(self.all_services, grid)

        return sw

    def set_defaults(self, box: Gtk.Box):
        self.notebook.append_page(self.groups_show(), Gtk.Label(label=_("Grouped")))
        self.notebook.append_page(self.all_services_show(), Gtk.Label(label=_("All services")))

    def prepare_services(self, sub_services=None):
        if not sub_services:
            sub_services = self.page_manager.machine.settings['services']

        services = {}
        for (group, datag) in sub_services.items():
            services[group] = {}
            for (service, title) in datag.items():
                try:
                    state = self.systemd.get_property(service, 'ActiveState')
                except DBusException:
                    state = "inactive"
                    print("NOTL: :( %s" % service)

                services[group][service] = {
                    'title': str(title),
                    'state': str(state),
                    'switch': Gtk.Switch(),
                    'spinner': Gtk.Spinner(),
                }
        return services

    def get_services_completed(self):
        if not self._services_completed:
            self._services_completed = self.prepare_services()
        return self._services_completed

    def build_table(self, services=None, grid=None):
        machine = self.page_manager.machine
        builder = self.page_manager.builder
        if not grid:
            grid = self.grid

        if not services:
            services = self.get_services_completed()

        if services:
            prev = None
            keys = list(sorted(services.keys()))
            for group in keys:
                datag = services[group]

                group_name = Gtk.Label(label=group)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

                # if self.uid == 0:
                stop_all_button = Gtk.Button.new_from_icon_name("media-playback-stop", Gtk.IconSize.BUTTON)
                start_all_button = Gtk.Button.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
                start_all_button.group = group
                stop_all_button.group = group

                start_all_button.connect("clicked", lambda widget: self.process_group_services_now(True, widget.group))
                stop_all_button.connect("clicked", lambda widget: self.process_group_services_now(False, widget.group))

                self.protected_widgets.append(start_all_button)
                self.protected_widgets.append(stop_all_button)

                box.add(start_all_button)
                box.add(stop_all_button)

                if not prev:
                    grid.add(group_name)
                else:
                    grid.attach_next_to(group_name, prev, Gtk.PositionType.BOTTOM, 1, 1)
                grid.attach_next_to(box, group_name, Gtk.PositionType.RIGHT, 1, 1)
                prepre = None
                for (service, data) in datag.items():
                    switch = data['switch']
                    spinner = data['spinner']
                    switch.set_active(data['state'] == 'active')
                    switch.connect("notify::active", self.work_with_service, services)
                    self.protected_widgets.append(switch)
                    label = Gtk.Label(label=data['title'], xalign=0)

                    if not prepre:
                        prepre = True
                        grid.attach_next_to(switch, group_name, Gtk.PositionType.BOTTOM, 1, 1)
                    else:
                        grid.attach_next_to(switch, prev, Gtk.PositionType.BOTTOM, 1, 1)
                    grid.attach_next_to(label, switch, Gtk.PositionType.RIGHT, 1, 1)
                    grid.attach_next_to(spinner, label, Gtk.PositionType.RIGHT, 1, 1)
                    prev = switch

    def process_group_services_now(self, action, group_name):
        services = self.get_services_completed()
        for (group, gdata) in services.items():
            if group == group_name:
                for (service, data) in gdata.items():
                    if data['switch'].get_active() != action:
                        data['switch'].set_active(action)

    switches_service_lock = False

    def preserved_switch(self, switcher, state):
        self.switches_service_lock = True
        switcher.set_state(state)
        self.switches_service_lock = False

    def work_with_service(self, switch, x, services=None):

        if not services:
            services = self.get_services_completed()

        if not self.switches_service_lock:
            for (group, datag) in services.items():
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

    def systemd_job_removed(self, arg1, path, service, status):
        for (group, datag) in self.all_services.items():
            for (servicein, data) in datag.items():
                spinner = data["spinner"]
                if servicein == service:
                    if status == 'done':
                        spinner.stop()
                        res = self.systemd.get_property(servicein, 'ActiveState')
                        if res == 'active':
                            self.preserved_switch(data['switch'], True)
                        else:
                            self.preserved_switch(data['switch'], False)