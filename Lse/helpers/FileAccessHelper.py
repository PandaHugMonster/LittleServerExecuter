#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import os
_work_directory = None


class FileAccessHelper:
    @staticmethod
    def work_directory():
        global _work_directory
        if not _work_directory:
            _work_directory = os.path.dirname(os.path.abspath(__file__ + "/../../"))
        return _work_directory

    @staticmethod
    def get_logo(alias="empty"):
        alias = alias.lower()
        if alias == "empty":
            path = FileAccessHelper.get_image("ui/images/empty.svg")
        else:
            path = FileAccessHelper.get_image("ui/images/logos/" + alias + ".svg")
        return path

    @staticmethod
    def get_image(subpath):
        return os.path.abspath(FileAccessHelper.work_directory() + "/" + subpath)

    @staticmethod
    def get_ui(name):
        return os.path.abspath(FileAccessHelper.work_directory() + "/ui/" + name + ".ui")
