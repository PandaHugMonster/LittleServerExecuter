#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import gi

from Lse import AbstractPage
from Lse.models import AbstractMachine

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk


class PageManager:

    _app = None
    _header = None
    _machine = None

    _name_index = {}
    _pages = []

    def __init__(self, machine: AbstractMachine, app):
        self._app = app
        self._header = Gtk.HeaderBar.new()
        self._machine = machine

    def add_page(self, page: AbstractPage) -> bool:
        size = len(self._pages)
        title = page.title

        if size:
            for name in self._name_index:
                if title == name:
                    return True

        self._pages.insert(size, page)
        self._name_index[title] = size
        page.page_manager = self

        return True

    @property
    def machine(self) -> AbstractMachine:
        return self._machine

    @property
    def header(self) -> Gtk.HeaderBar:
        return self._header

    @property
    def pages(self) -> list:
        return self._pages

    def get_page(self, name: str) -> AbstractPage:
        index = self._name_index[name]
        return self._pages[index]

    @property
    def builder(self) -> Gtk.Builder:
        return self._app.builder
