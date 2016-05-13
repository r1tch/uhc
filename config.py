#!/usr/bin/env python3

import configparser
import logging

class Config(configparser.ConfigParser):
    def __init__(self, local_dir):
        super().__init__()
        self.set_default_values()
        self.read(local_dir + "/config.ini")

    def set_default_values(self):
        self.add_section("logging")
        # we expect numerical values here
        # -- see logging's source (DEBUG=10, INFO=20, WARNING=30, ERROR=40)
        self.set("logging", "level", str(logging.DEBUG))     # to be replaced by WARNING after prod release

        self.add_section("remote")
        self.set("remote", "port", str(8888))

        self.add_section("mios")
        self.set("mios", "host", "10.0.1.51")
        self.set("mios", "update_frequency_secs", "3")

        self.add_section("kodi")
        self.set("kodi", "host", "10.0.1.27")   # osmc2
        self.set("kodi", "port", "9090")
        self.set("kodi", "reconnectTimeout", "5")

        self.add_section("paradox")
        self.set("paradox", "device", "/dev/ttyAMA0")  # RPi default

