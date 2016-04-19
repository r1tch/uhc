#!/usr/bin/env python3

class Service:
    """Base class for all services"""
    def __init__(self, container):
        self.container = container
        self.container.services[self.id()] = self

    def broadcast(self, msgDict):
        for service in self.container.services.values():
            if service != self:         # do not send to self - we should use methods to do stuff privately
                service.msg(self, msgDict)

    def sendTo(self, toServiceId, msgDict):
        if toServiceId not in self.container.services:
            return

        toService = self.container.services[toServiceId]
        toService.msg(self, msgDict)

    def id(self):
        """Should return a unique ID"""
        raise NotImplementedError

    def msg(self, fromService, msgDict):
        """Sends a message (dict) to this service - response also happens via msg call(s)"""
        raise NotImplementedError

