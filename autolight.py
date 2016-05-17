#!/usr/bin/env python3

import logging

from schedule import Schedule
from service import Service
    
class AutoLight(Service):
    """Automates lights, flashes alarms"""

    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.eventloop = eventloop
        self.onoffHandle = None
        self.nextStateHandle = None
        self.flashStateNowOn = False

    #@override
    def id(self):
        return "autolight"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "EntryDelayStarted":
            self._batchSetLevel("entrylights", 100)

        elif msgDict["msg"] == "initiateFlashAlarm":
            self._initiateFlashAlarm()

        elif msgDict["msg"] == "stopFlashAlarm":
            self._stopFlashAlarm()

    def _batchSetLevel(self, configtag, level):
        shades = self.config.get("autolight", configtag)
        for shade in shades.split(','):
            self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": level })

    def _stopFlashAlarm(self):
        logging.info("Stopping flashAlarm")
        self._newState("off")

    def _initiateFlashAlarm(self):
        if self.controller.state.flashAlarmState != "off":
            logging.info("flashAlarm already active - not reinitiating")
            return

        logging.info("Initiated flashAlarm")
        self._nextFlashAlarmState()


    def _nextFlashAlarmState(self):
        if self.flashAlarmState == "off":
            self._newState("delay")
            self.nextStateHandle = self.eventloop.call_later(self.config.get("autolight", "flashAlarmDelaySecs"), self._nextFlashAlarmState)

        elif self.flashAlarmState == "delay":
            self._newState("preflash")
            self.nextStateHandle = self.eventloop.call_later(self.config.get("autolight", "flashAlarmDelaySecs"), self._nextFlashAlarmState)

        elif self.flashAlarmState == "pref":
            self._newState("full")


    def _cancelTimers(self):
        if self.onoffHandle:
            self.onoffHandle.cancel()

        if self.nextStateHandle:
           self.nextStateHandle.cancel()

    def _doFlash(self):
        lights = ""
        if state == "preflash":
            shades = self.config.get("autolight", "flashAlarmPreflash")
        elif state == "full":
            shades = self.config.get("autolight", "flashAlarmFull")
        else:
            logging.error("doFlash while state is {}".format(state))
            return

        self.flashStateNowOn = not self.flashStateNowOn

        level = 0
        if self.flashStateNowOn:
            level = 100

        self._batchSetLevel(shades, level)
        self.onoffHandle = self.eventloop.call_later(self.config.getfloat("autolight", "flashAlarmOnOffDelaySecs"), self._doFlash)


    def _newState(self, state):
        self.controller.state.flashAlarmState = state
        self.broadcast({ "msg": "flashAlarm", "state": state })

        if state == "off":
            self._cancelTimers()
        elif state == "delay":
            self._cancelTimers()
        elif state == "preflash" or state == "full":
            self._doFlash()



