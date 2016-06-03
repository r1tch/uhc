#!/usr/bin/env python3

# just storing the state; continuous updates are sent via individual msgs
# (eg, ExitDelayStarted when about to leave, Armed when left home)
class State:
    """Common object accessible by all services, to store current states"""
    def __init__(self):
        self.atHome = False   # we're home if alarm system is unarmed
        self.asleep = False  # detected based on movements around the house
        self.flashAlarmState = "off"    # "delay", "preflash", "full"
        self.guestHost = False # if true, no automation when home
        self.hifiOn = False

    def dictState(self):
        ret = dict()
        ret["atHome"] = self.atHome
        ret["asleep"] = self.asleep
        ret["flashAlarmState"] = self.flashAlarmState
        ret["hifiOn"] = self.hifiOn

        return ret

