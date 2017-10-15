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
    def prepare_content(self):
        return Gtk.Notebook.new()
