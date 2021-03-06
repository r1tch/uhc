#!/usr/bin/env python3

import logging

from service import Service

class HiFi(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.controller = controller

    #@override
    def id(self):
        return "hifi"

    #@override
    def msg(self, fromService, msgDict):
        if "msg" not in msgDict:
            return

        if msgDict["msg"] == "Disarmed":
            self._hifiOn()

        elif msgDict["msg"] == "ExitDelayStarted":
            self._hifiOff()

        elif msgDict["msg"] == "Awakened":
            self._hifiOn()

        elif msgDict["msg"] == "Asleep":
            self._hifiOff()

        elif msgDict["msg"] == "hifiOn":
            self._hifiOn()

        elif msgDict["msg"] == "hifiOff":
            self._hifiOff()

        elif msgDict["msg"] == "hifiVolUp":
            self._sendCommand("volup")

        elif msgDict["msg"] == "hifiVolDn":
            self._sendCommand("voldn")

        elif msgDict["msg"] == "setMediaSource":
            self._hifiMediaSource()

    def _hifiOn(self):
        self._sendCommand("on")
        self.controller.state.hifiOn = True

    def _hifiOff(self):
        self._hifiMediaSource()         # reason: not to turn loud radio on upon awakening
        self._sendCommand("off")
        self.controller.state.hifiOn = False

    def _hifiMediaSource(self):
        command = self.config.get("hifi", "mediaSourceCommand")
        self._sendCommand(command)

    def _sendCommand(self, command):
        remote = self.config.get("hifi", "remote")
        self.sendTo("irtrans", {"msg": "irsend", "remote": remote, "command": command})

