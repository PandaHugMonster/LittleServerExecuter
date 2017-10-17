#!/bin/python3
# -*- coding: utf-8 -*-
# Author: PandaHugMonster <ivan.ponomarev.pi@gmail.com>
# Version: 0.4
import sys

from Lse import LseApp

app = LseApp()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
