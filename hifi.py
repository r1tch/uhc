#!/usr/bin/env python3

import logging

from service import Service

class HiFi(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.eventloop = eventloop

    #@override
    def id(self):
        return "hifi"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "Disarmed":
            self._sendCommand("on")

        elif msgDict["msg"] == "ExitDelayStarted":
            self._sendCommand("off")

        elif msgDict["msg"] == "Awakened":
            self._sendCommand("on")

        elif msgDict["msg"] == "Asleep":
            self._sendCommand("off")

        elif msgDict["msg"] == "hifiOn":
            self._sendCommand("on")

        elif msgDict["msg"] == "hifiOff":
            self._sendCommand("off")

        elif msgDict["msg"] == "hifiVolUp":
            self._sendCommand("volup")

        elif msgDict["msg"] == "hifiVolDn":
            self._sendCommand("voldn")

        elif msgDict["msg"] == "setMediaSource":
            command = self.config.get("hifi", "mediaSourceCommand")
            self._sendCommand(command)

    def _sendCommand(self, command):
        remote = self.config.get("hifi", "remote")
        self.sendTo("irtrans", {"msg": "irsend", "remote": remote, "command": command})

