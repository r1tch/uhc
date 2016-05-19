#!/usr/bin/env python3

import datetime
import logging
import random
import time

from schedule import Schedule
from service import Service
    
class AutoShade(Service):
    """Automates shade movement (arrival/leaving, when alone, etc)"""

    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.eventloop = eventloop
        self.sunrise = 0
        self.sunset = 0
        self.morningOpenDone = False

    #@override
    def id(self):
        return "autoshade"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "SunRiseSet":
            self.morningOpenDone = False
            self.sendTo("schedule", {"msg": "cancelMyEvents"})  # enabling rescheduling all events

            self.sunrise = msgDict["sunrise"]
            self.sunset = msgDict["sunset"]
            self.sendTo("schedule", {"msg": "newEvent", "at": self._duskTime(), "deferredMsg": {"msg": "duskClose"}, "desc": "Closing shades at dusk when home"})
            self.sendTo("schedule", {"msg": "newEvent", "at": self.config.hhmmts("autoshade", "nightclosetime"), "deferredMsg": {"msg": "nightClose"}, "desc": "Closing shades at late night when home"})
            if self._isSummerTime():
                self.sendTo("schedule", {"msg": "newEvent", "at": self.config.hhmmts("autoshade", "summerfloweropentime"), "deferredMsg": {"msg": "flowerOpen"}, "desc": "Opening shades only in the afternoon to keep the house cool"})
            else:
                opentime = self.sunrise + random.randint(0, 90*60)
                self.sendTo("schedule", {"msg": "newEvent", "at": opentime, "deferredMsg": {"msg": "flowerOpen"}, "desc": "Opening shades in the morning"})

            closetime = self.sunset - random.randint(0, 90*60)
            self.sendTo("schedule", {"msg": "newEvent", "at": closetime, "deferredMsg": {"msg": "flowerClose"}, "desc": "Closing shades in the evening"})

        elif msgDict["msg"] == "Disarmed":
            if self._isLight():
                self._batchUpDown("entryopen", 100)

        elif msgDict["msg"] == "ExitDelayStarted":
            self._batchUpDown("exitclose", 0)
            openDelay = random.randint(60*15, 60*60)
            now = time.time()
            threePM = self.config.hhmmts("autoshade", "summerfloweropentime")
            openTimestamp = now + openDelay
            if self._isLight(openTimestamp) and (not self._isSummerTime() or now > threePM):
                self.sendTo("schedule", {"msg": "newEvent", "at": openTimestamp, "deferredMsg": {"msg": "flowerClose"}, "desc": "Closing shades in the evening [after leave]"})
        
        elif msgDict["msg"] == "ZoneOpen":
            now = time.time()
            if (msgDict["zoneid"] == self.config.getint("autoshade", "morningopenzone") and
                    self._isLight() and
                    self.controller.state.atHome and 
                    not self.controller.state.guestHost and 
                    not self.morningOpenDone and
                    self.config.hhmmts("autoshade", "morningopenfrom") < now and
                    self.config.hhmmts("autoshade", "morningopento") > now):
                self._batchUpDown("morningopen", 100)
                self.morningOpenDone = True
        
        elif msgDict["msg"] == "duskClose":
            self._duskClose()
        elif msgDict["msg"] == "flowerOpen":
            self._flowerOpen()
        elif msgDict["msg"] == "flowerClose":
            self._flowerClose()
        elif msgDict["msg"] == "nightClose":
            self._nightClose()

    # duskClose: athome & sunset - 15min
    # morningOpen: >6AM zonetriggered wakeup -- morningOpenDone = True
    # away: sunrise & sunset +- random interval

    def _batchUpDown(self, shadesConfig, level):
        shades = self.config.get("autoshade", shadesConfig)
        for shade in shades.split(','):
            self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": level })

    def _isDark(self, when = 0):
        if not when:
            when = time.time()
        return when < self.sunrise or when > self.sunset

    def _isLight(self, when = 0):
        if not when:
            when = time.time()
        return not self._isDark(when)

    def _flowerOpen(self):
        if self.controller.state.atHome:
            logging.debug("flowerOpen: not opening, back home again")
            return
        if self._isDark():
            return
        self._batchUpDown("floweropen", 100)

    def _flowerClose(self):
        if self.controller.state.atHome:
            logging.debug("flowerClose: not closing, back home again")
            return
        if self._isLight():
            return
        self._batchUpDown("flowerclose", 0)

    def _duskClose(self):
        if not self.controller.state.atHome:
            logging.debug("duskClose: not closing, not at home")
            return
        self._batchUpDown("duskclose", 0)

    def _nightClose(self):
        if not self.controller.state.atHome:
            logging.debug("nightClose: not closing, not at home")
            return
        self._batchUpDown("nightclose", 0)

    def _duskTime(self):
        return self.sunset - 15*60;

    def _dawnTime(self):
        return self.sunrise + 15*60;

    def _isSummerTime(self):
        month = datetime.datetime.now().month
        return month >= 6 and month <= 8        # no need to configure, experience shows no excess heat outside Jun-Jul-Aug


