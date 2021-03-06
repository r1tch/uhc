#!/usr/bin/env python3

import logging
import requests
import threading

from service import Service
from .nodes import ZWaveNodes
from .miosnodelistquery import ZWaveMiosNodelistQuery
from .miosstatusupdate import ZWaveMiosStatusUpdate
from .miosrequest import ZWaveMiosRequest

class ZWaveMios(Service):
    def __init__(self, container, config, eventloop):
        super().__init__(container)
        self.config = config
        self.eventloop = eventloop
        self.zwavenodes = None
        self.nodelistquery = ZWaveMiosNodelistQuery(config, eventloop, self._gotNodes)
        self.statusupdate = ZWaveMiosStatusUpdate(config, eventloop, self._statusCallback)
        self.request = ZWaveMiosRequest(config, eventloop, self._statusCallback)
        self.levels = {}

    # @override
    def id(self):
        return "zwave"

    # @override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "newConnection":
            response = self._allNodesMsg()
            response["id"] = msgDict["id"]
            fromService.msg(self, response)
        elif msgDict["msg"] == "getNodes":
            response = self._allNodesMsg()
            response["origMsg"] = msgDict
            fromService.msg(self, response)
        elif msgDict["msg"] == "setLevel":
            if "level" not in msgDict:
                return

            logging.debug("SETL {}".format(msgDict))
            if "nodeid" in msgDict:
                self.request.setLevel(int(msgDict["nodeid"]), int(msgDict["level"]))

            if "name" in msgDict:
                self.request.setLevelByName(msgDict["name"], int(msgDict["level"]))
        elif msgDict["msg"] == "stopLevelChange":
            if "nodeid" in msgDict:
                self.request.stopLevelChange(int(msgDict["nodeid"]))
            if "name" in msgDict:
                self.request.stopLevelChangeByName(msgDict["name"])

        elif msgDict["msg"] == "setAllLights":
            if "level" in msgDict:
                self.request.setAllLights(int(msgDict["level"]))

        elif msgDict["msg"] == "turnOnOnlyLights":
            if "names" in msgDict:
                lightsToBeOn = set(msgDict["names"].split(','))
                self.request.turnOnOnlyLights(lightsToBeOn)

    def _allNodesMsg(self):
        return { "msg": "gotNodes", "nodes": self.zwavenodes.allNodes()}

    def _gotNodes(self, zwavenodes):
        self.zwavenodes = zwavenodes
        
        self.statusupdate.setNodes(self.zwavenodes)
        self.request.setNodes(self.zwavenodes)

        self.broadcast(self._allNodesMsg())
        
        self.statusupdate.startUpdates()

    def _statusCallback(self, newlevels):
        changedLevels = {}

        for id in newlevels:
            if id not in self.zwavenodes.allIds():
                logging.error("Got level for unknown id '{}'".format(id))
                continue

            newlevel = newlevels[id]
            node = self.zwavenodes.byId(id)
            if newlevel != node.level:
                node.level = newlevel
                logging.info("New level for {} ({}): {}".format(id, node.name, newlevel))
                changedLevels[id] = newlevel

        if len(changedLevels):
            self.broadcast({ "msg": "changedLevels", "changedLevels": changedLevels })

