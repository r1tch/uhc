#!/usr/bin/env python3

class State:
    """Common object accessible by all services, to store current states"""
    def __init__(self, config):
        # TODO read state from file
        self.atHome = False   # we're home if alarm system is unarmed
        self.asleep = False  # detected based on movements around the house
        self.flashAlarmState = "off"    # "delay", "preflash", "full"
        self.guestHost = False # if true, no automation when home
        self.hifiOn = False
        self.projectorOn = False
        self.acOn = False
        self.acMode = "NANA24"
        self.scene = "none"
        self.tcpserver = None

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # TODO save state into file (/tmp - read config)
        if name != "tcpserver" and "tcpserver" in self.__dict__ and self.tcpserver:
            self.tcpserver.broadcastState(self.dictState())


    def dictState(self):
        ret = dict()
        ret["atHome"] = self.atHome
        ret["asleep"] = self.asleep
        ret["flashAlarmState"] = self.flashAlarmState
        ret["guestHost"] = self.guestHost
        ret["hifiOn"] = self.hifiOn
        ret["projectorOn"] = self.projectorOn
        ret["acOn"] = self.acOn
        ret["acMode"] = self.acMode
        ret["scene"] = self.scene

        return ret

