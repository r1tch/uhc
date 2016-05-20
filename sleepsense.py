#!/usr/bin/env python3

import logging

from service import Service

class SleepSense(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.eventloop = eventloop
        self.asleepTimer = None

    #@override
    def id(self):
        return "sleepsense"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "ZoneOpen":
            self._zoneOpen(msgDict["zoneid"])


    def _zoneOpen(self, zoneid):
        if not self._isBedroom(zoneid) and self.controller.state.asleep:
            self.controller.state.asleep = False
            self.broadcast({"msg": "Awakened"})
            logging.info("Woke up...")
            if self.asleepTimer:
                self.asleepTimer.cancel()
                self.asleepTimer = None
            return
            
        if self._isBedroom(zoneid) and not self.controller.state.asleep and not self.asleepTimer:
            self.asleepTimer = self.eventloop.call_later(self.config.getfloat("sleepsense", "fallAsleepTimeMinutes") * 60, self._fellAsleep)


    def _isBedroom(self, zoneid):
        bedrooms = self.config.get("sleepsense", "bedroomzones").split(",")
        if str(zoneid) in bedrooms:
            return True

        return False

    def _fellAsleep(self):
        self.broadcast({"msg": "Asleep"})
        self.asleepTimer = None
        self.controller.state.asleep = True
        logging.info("Fell asleep...")

