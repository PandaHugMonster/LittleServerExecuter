#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
from gi.repository import Gtk

from Lse.AbstractPage import AbstractPage


class PageInfo(AbstractPage):

    _title = "Machine Info"

    def __init__(self):
        super().__init__()

    @property
    def get_main_container(self) -> Gtk.Box:
        return self.page_manager.builder.get_object("InfoBox")

    @property
    def get_logo_place(self) -> Gtk.Image:
        return self.page_manager.builder.get_object("OSLogo")

    def set_defaults(self, box: Gtk.Box):
        machine = self.page_manager.machine
        print(machine)
        self.get_logo_place.set_from_file(machine.logo_path)
        self.page_manager.builder.get_object("place_machine_type").set_text(machine.type)
        self.page_manager.builder.get_object("place_hostname").set_text(machine.hostname)
        self.page_manager.builder.get_object("place_distrib").set_text(machine.distrib_name)
        self.page_manager.builder.get_object("place_arch").set_text(machine.architecture)
        self.page_manager.builder.get_object("place_platform").set_text(machine.platform)
        self.page_manager.builder.get_object("place_kernel").set_text(machine.version)
        self.page_manager.builder.get_object("place_date").set_text(str(machine.datetime))

    @property
    def prepare_content(self):
        box = self.get_main_container
        self.set_defaults(box)
        return box
