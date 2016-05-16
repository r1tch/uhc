#!/usr/bin/env python3

class ScheduledEvent:
    def __init__(self, id, fromServiceId, at, desc, deferredMsg):
        self.id = id
        self.fromServiceId = fromServiceId
        self.at = at
        self.desc = desc
        self.handle = None
        self.deferredMsg = deferredMsg

    def setHandle(self, handle):
        self.handle = handle

    def cancel(self):
        self.handle.cancel()
        
