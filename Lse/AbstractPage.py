#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
from abc import ABCMeta, abstractmethod

from gi.overrides import Gtk

from Lse import PageManager


class AbstractPage:
    __metaclass__ = ABCMeta

    _title = None
    _content = None
    _page_manager = None

    def __init__(self):
        pass

    @property
    def page_manager(self) -> PageManager:
        return self._content

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
    def title(self) -> str:
        return self._title
