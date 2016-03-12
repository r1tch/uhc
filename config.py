#!/usr/bin/env python3

import configparser
import logging

config = None

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

        self.add_section("TODO_New_Section")







