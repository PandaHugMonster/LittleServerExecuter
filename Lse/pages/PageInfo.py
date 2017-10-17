#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import gettext
import os

from gi.repository import Gtk

from Lse.AbstractPage import AbstractPage
from Lse.helpers import FileAccessHelper

localedir = os.path.join(FileAccessHelper.work_directory(), 'locale')
translate = gettext.translation("pages", localedir)
_ = translate.gettext


class PageInfo(AbstractPage):

    def __init__(self):
        name = "page_info"
        title = _("Machine Info")
        super().__init__(name, title)

    @property
    def get_main_container(self) -> Gtk.Box:
        return self.page_manager.builder.get_object("InfoBox")

    @property
    def get_logo_place(self) -> Gtk.Image:
        return self.page_manager.builder.get_object("OSLogo")

    def set_defaults(self, box: Gtk.Box):
        machine = self.page_manager.machine
        self.get_logo_place.set_from_file(machine.logo_path)
        self.page_manager.builder.get_object("place_machine_type").set_text(machine.type)
        self.page_manager.builder.get_object("place_hostname").set_text(machine.hostname)
        self.page_manager.builder.get_object("place_distrib").set_text(machine.distrib_name)
        self.page_manager.builder.get_object("place_arch").set_text(machine.architecture)
        self.page_manager.builder.get_object("place_platform").set_text(machine.platform)
        self.page_manager.builder.get_object("place_kernel").set_text(machine.version)
        self.page_manager.builder.get_object("place_date").set_text(str(machine.datetime))