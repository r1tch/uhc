#!/usr/bin/env python3

import datetime
import logging
import time

from scheduledevent import ScheduledEvent
from service import Service
    
# purpose: abstraction of scheduled events, give a chance to cancel them + reschedule them (eg, by doing "new day" manually)
class Schedule(Service):
    """Schedules an msg to be sent at given time"""

    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.eventloop = eventloop
        self.events = dict()
        self.nextEventId = 1
        self.midnightHandle = None
        
        self.eventloop.call_later(1, self.sendNewDay)   # upon startup, always initialize services

    #@override
    def id(self):
        return "schedule"

    # returns a message defined in "deferredMsg" param, sending to originating service
    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "newEvent":
            delay = float(0)
            if "at" in msgDict:
                delay = float(msgDict["at"]) - time.time()
            elif "delay" in msgDict:
                delay = float(msgDict["delay"])
            else:
                logging.error('newEvent needs "at" or "delay" param')
                return

            if "deferredMsg" not in msgDict:
                logging.error('newEvent needs "deferredMsg" param')
                return

            if "desc" not in msgDict:
                logging.error('newEvent needs "desc" param')
                return

            if delay <= 0:
                logging.info('{} attempted to schedule an event in the past on "{}"'.format(fromService.id(), msgDict["desc"]))
                return

            if delay > 24 * 60 * 60:    # not planning more than 1 day
                logging.info('{} attempted to schedule an event too far in the future on "{}"'.format(fromService.id(), msgDict["desc"]))
                return

            at = time.time() + delay
            event = ScheduledEvent(self.nextEventId, fromService.id(), at, msgDict["desc"], msgDict["deferredMsg"])
            handle = self.eventloop.call_later(delay, self._triggerEvent, event)
            event.setHandle(handle)
            self.events[self.nextEventId] = event
            self.nextEventId += 1

        elif msgDict["msg"] == "getScheduledEvents":
            responseMsg = { "msg": "scheduledEvents", "events": self.events, "origMsg": msgDict }
            self.sendTo(fromService.id(), responseMsg)

        elif msgDict["msg"] == "cancelEvent":
            if "eventId" in msgDict:
                self._cancelEvent(msgDict["eventId"])

        elif msgDict["msg"] == "cancelMyEvents":
            herEventIds = [ event.id for event in self.events.values() if event.fromServiceId == fromService.id() ]
            for id in herEventIds:
                print("DEBUG remove {} {}".format(self.events[id].fromServiceId, self.events[id].desc))
                self._cancelEvent(id)
        
        elif msgDict["msg"] == "sendNewDay":
            self.sendNewDay()


    def sendNewDay(self):
        logging.info("New day: {}".format(datetime.datetime.now()))
        self.broadcast({"msg":"newDay"})

        if self.midnightHandle:
            self.midnightHandle.cancel()   # in case this is an intraday request to reschedule everything

        delay = Schedule._secsToNextMidnight()
        self.midnightHandle = self.eventloop.call_later(delay, self.sendNewDay)

    def _triggerEvent(self, event):
        logging.debug("Event triggered: {}".format(event.desc))
        if event in self.events:
            del self.events[event]
        self.sendTo(event.fromServiceId, event.deferredMsg)

    def _cancelEvent(self, eventId):
        if eventId not in self.events:
            return
        self.events[eventId].cancel()
        del self.events[eventId]

    def _secsToNextMidnight(nowTimestamp = 0):

        if not nowTimestamp:
            nowTimestamp = int(time.time())

        now = datetime.datetime.fromtimestamp(nowTimestamp)
        todayMidnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        nextMidnight = todayMidnight + datetime.timedelta(days=1)

        return nextMidnight.timestamp() - nowTimestamp


if __name__ == "__main__":
    now = datetime.datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    print(repr(now))

    day = datetime.datetime(2013, 3, 31)

    oneday = datetime.timedelta(days=1)
    timestamp = day.timestamp()
    print(repr(day), timestamp)
    day += oneday
    timestamp2 = day.timestamp()
    # interesting; at the end this will correctly print 23 hrs difference, due to DST change (per doc, naive mode relies on mktime, which is smart apparently)
    print(repr(day), timestamp2, (timestamp2-timestamp) / 60 / 60)

    testDayTs = datetime.datetime(2013, 3, 31, 0, 30).timestamp()
    print(Schedule._secsToNextMidnight(testDayTs) / 60.0 / 60.0)


