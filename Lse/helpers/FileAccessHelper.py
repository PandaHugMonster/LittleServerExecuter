#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import json
import os
from pathlib import Path

_work_directory = None


class FileAccessHelper:
	@staticmethod
	def work_directory():
		global _work_directory
		if not _work_directory:
			_work_directory = os.path.dirname(os.path.abspath(__file__ + "/../../"))
		return _work_directory

	@staticmethod
	def get_logo(alias="empty", subtype="distrib-logo"):
		alias = alias.lower()
		if alias == "empty":
			path = FileAccessHelper.get_image("ui/images/empty.svg")
		else:
			path = FileAccessHelper.get_image("ui/images/logos/" + subtype + "-" + alias + ".svg")
		return path

	@staticmethod
	def get_image(subpath):
		return os.path.abspath(FileAccessHelper.work_directory() + "/" + subpath)

	@staticmethod
	def get_ui(name):
		return os.path.abspath(FileAccessHelper.work_directory() + "/ui/" + name)

	@staticmethod
	def get_settings_path(settings_file="settings"):
		work_directory = FileAccessHelper.work_directory()
		settings_file += ".json"
		sub_path = os.path.join(Path.home(), ".lse/" + settings_file)
		if not os.path.isfile(sub_path):
			sub_path = os.path.join(work_directory, "/etc/lse/" + settings_file)
			if not os.path.isfile(sub_path):
				sub_path = os.path.join(work_directory, "extras/" + settings_file)

		return os.path.abspath(sub_path)

	@staticmethod
	def save(file: str, content: str):
		f = open(file, "w")
		f.write(content)
		f.close()

	@staticmethod
	def delete(file: str):
		os.remove(file)

	@staticmethod
	def isexist(file: str):
		return Path(file).exists()

	@staticmethod
	def load_settings(settings_path: str):
		json_data = open(settings_path)
		_settings = json.load(json_data)
		json_data.close()
		return _settings

	@staticmethod
	def save_settings(settings_path: str, settings):
		json_data = open(settings_path, 'w')
		json.dump(settings, json_data)
		json_data.close()

