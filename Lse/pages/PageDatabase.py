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


class PageDatabase(AbstractPage):
    notebook = None

    def __init__(self):
        name = "page_database"
        title = _("Database Server")
        super().__init__(name, title)

    @property
    def get_main_container(self) -> Gtk.Box:
        if not self.notebook:
            self.notebook = Gtk.Notebook.new()
        return self.notebook

    def set_defaults(self, box: Gtk.Box):
        scroll_view = Gtk.ScrolledWindow()
        config_view = Gtk.TextView()
        scroll_view.add(config_view)
        self.notebook.append_page(scroll_view, Gtk.Label(label=_("Mysql Config View")))
        txtbuf = config_view.get_buffer()

        confpath = "/etc/mysql/"
        result = ""
        with open(os.path.join(confpath, "my.cnf")) as f:
            for line in f:
                result += line

        txtbuf.set_text(result)
