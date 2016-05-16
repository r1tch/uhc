#!/usr/bin/env python3

import datetime
import logging

from service import Service
from suncalc import SunCalc

class SunRiseSet(Service):
    """Generates events for sunrise and sunset"""
    def __init__(self, container, config, eventloop):
        super().__init__(container)
        self.eventloop = eventloop
        lat = config.getfloat("location", "latitude")
        lon = config.getfloat("location", "longitude")
        self.sunCalc = SunCalc(lat, lon)

    #@override
    def id(self):
        return "sunriseset"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "newDay":
            now = datetime.datetime.now()
            sunrise = self.sunCalc.sunrise(now)
            sunset = self.sunCalc.sunset(now)

            sunriseStr = datetime.datetime.fromtimestamp(sunrise).strftime('%H:%M')
            sunsetStr = datetime.datetime.fromtimestamp(sunset).strftime('%H:%M')
            logging.info("Sunrise: {}, sunset: {}".format(sunriseStr, sunsetStr))
            
            self.broadcast({"msg":"sunRiseSet", "sunrise": sunrise, "sunset": sunset})

            #self.sendTo("schedule", {"msg": "addSchedule", "at": sunset, "deferredMsg": {"msg": "test"}, "desc": "just a test" })
            #self.sendTo("schedule", {"msg": "cancelMyEvents"})


