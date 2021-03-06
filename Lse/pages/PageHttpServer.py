#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import os

from gi.repository import Gtk

from Lse.AbstractPage import AbstractPage


class PageHttpServer(AbstractPage):
    notebook = None

    def __init__(self):
        name = "page_http_server"
        title = "HTTP Server"
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
        self.notebook.append_page(scroll_view, Gtk.Label(label="Apache Config View"))
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
        self.notebook.append_page(scroll, Gtk.Label(label="List of modules"))
        # rep = self.notebook.get_nth_page(0)
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
