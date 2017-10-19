#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import gettext
import os
from pathlib import Path

from gi.repository import Gtk

from Lse.AbstractPage import AbstractPage
from Lse.helpers import FileAccessHelper

localedir = os.path.join(FileAccessHelper.work_directory(), 'locale')
translate = gettext.translation("pages", localedir)
_ = translate.gettext


class PageHttpServer(AbstractPage):
    work_dir = "/etc/httpd"
    notebook = None

    def __init__(self):
        name = "page_http_server"
        title = _("HTTP Server")
        super().__init__(name, title)

    @property
    def get_main_container(self) -> Gtk.Box:
        if not self.notebook:
            self.notebook = Gtk.Notebook.new()
        return self.notebook

    def process_line(self, line=""):
        if line == "\n":
            return ""

        res = ""
        tmp_line = line.replace(" ", "")

        if tmp_line[0][:1] != "#":
            sub_res = ""
            splitted = line.split(" ")
            if splitted:
                other = ""
                if len(splitted) > 1:
                    command = splitted[0]
                    other = splitted[1]
                else:
                    command = splitted[0]

                if command.lower() == "include":
                    other = other.replace("\n", "")
                    if other[0] != "/":
                        other = "%s/%s" % (self.work_dir, other)
                    if Path(other).is_file():
                        sub_res += "\n##\n## Included from: %s\n##\n" % other
                        with open(other) as f:
                            for sline in f:
                                sub_res += self.process_line(sline)
                        res += sub_res
                    else:
                        res += "\n##\n## File does not exist: %s\n##\n" % other
                else:
                    res += line
            else:
                res += line

        return res

    def config_show(self):
        config_view = Gtk.TextView()

        scroll_view = Gtk.ScrolledWindow()
        scroll_view.add(config_view)

        txtbuf = config_view.get_buffer()
        confpath = "%s/conf/" % self.work_dir
        result = ""
        with open(os.path.join(confpath, "httpd.conf")) as f:
            for line in f:
                result += self.process_line(line)
        txtbuf.set_text(result)

        return scroll_view

    def modules_show(self):
        scroll = Gtk.ScrolledWindow()
        colbox = Gtk.Grid()
        colbox.set_border_width(20)
        colbox.set_row_homogeneous(True)
        colbox.set_row_spacing(10)
        colbox.set_column_spacing(10)
        scroll.add(colbox)
        # rep = self.notebook.get_nth_page(0)
        # rep.pack_start(scroll)

        modpath = "%s/modules/" % self.work_dir
        c = r = 0
        for fil in list(sorted(os.listdir(modpath))):
            if os.path.isfile(os.path.join(modpath, fil)):
                colbox.attach(Gtk.Label(label=fil, xalign=0), c, r, 1, 1)

            if (c + 1) % 3 == 0:
                r += 1
                c = 0
            else:
                c += 1

        return scroll

    def set_defaults(self, box: Gtk.Box):
        self.notebook.append_page(self.config_show(), Gtk.Label(label=_("Apache Config View")))
        self.notebook.append_page(self.modules_show(), Gtk.Label(label=_("List of modules")))
