#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
from abc import ABCMeta, abstractmethod

from gi.repository import Gtk

from Lse import PageManager


class AbstractPage:
    __metaclass__ = ABCMeta

    _title = None
    _content = None
    _page_manager = None

    @property
    def page_manager(self) -> PageManager:
        return self._page_manager

    @page_manager.setter
    def page_manager(self, val: PageManager):
        self._page_manager = val

    @property
    def content(self) -> Gtk.Container:
        if not self._content:
            self._content = self.prepare_content
        return self._content

    @property
    @abstractmethod
    def prepare_content(self) -> Gtk.Container:
        pass

    @property
    def title(self):
        return self._title
