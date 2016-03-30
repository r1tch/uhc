#!/usr/bin/env python3

import logging
import requests
import threading

from service import Service
from .nodes import ZWaveNodes
from .miosnodelistquery import ZWaveMiosNodelistQuery
from .miosstatusupdate import ZWaveMiosStatusUpdate

class ZWaveMios(Service):
    def __init__(self, container, config, eventloop):
        super(container)
        self.config = config
        self.eventloop = eventloop
        self.zwavenodes = None
        self.nodelistquery = ZWaveMiosNodelistQuery(config, eventloop, self.gotNodes)
        self.statusupdate = ZWaveMiosStatusUpdate(config, eventloop, self.statusCallback)
        self.levels = {}

    # @override
    def id(self):
        return "zwave"

    def execute(self, command):
        # TODO turn stuff on-off
        raise NotImplementedError

    def gotNodes(self, zwavenodes):
        self.zwavenodes = zwavenodes
        # TODO notify listeners about new node list
        self.statusupdate.setNodes(self.zwavenodes)

        for listener in self.listeners:
            listener.zwaveGotNodes(zwavenodes.allNodes())
        
        self.statusupdate.startUpdates()

    def statusCallback(self, newlevels):
        changedLevels = {}

        for id in newlevels:
            newlevel = newlevels[id]
            if not id in self.levels or newlevel != self.levels[id]:
                self.levels[id] = newlevel
                name = self.zwavenodes.byId(id).name
                logging.info("New level for {} ({}): {}".format(id, name, newlevel))
                changedLevels[id] = newlevel

        for listener in self.listeners:
            listener.zwaveChangedLevels(changedLevels)


