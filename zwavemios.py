#!/usr/bin/env python3

import logging
import requests
import threading

from zwavenodes import ZWaveNodes
from zwavemiosnodelistquery import ZWaveMiosNodelistQuery
from zwavemiosstatusupdate import ZWaveMiosStatusUpdate

class ZWaveMios:
    def __init__(self, config, eventloop):
        self.config = config
        self.eventloop = eventloop
        self.zwavenodes = ZWaveNodes()
        self.nodelistquery = ZWaveMiosNodelistQuery(config, eventloop, self.gotNodes)
        self.statusupdate = ZWaveMiosStatusUpdate(config, eventloop, self.statusCallback)
        self.listeners = []

    def gotNodes(self, zwavenodes):
        self.zwavenodes = zwavenodes
        # TODO notify listeners about new node list
        self.statusupdate.startUpdates()

    def statusCallback(self, newlevels):
        # TODO notify listeners -- only about changes? yes!
        pass

