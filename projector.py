#!/usr/bin/env python3

import logging

from service import Service

class Projector(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.controller = controller

    #@override
    def id(self):
        return "projector"
    
    #@override
    def msg(self, fromService, msgDict):
        if "msg" not in msgDict:
            return

        if msgDict["msg"] == "projectorOn":
            self._projectorOn()

        if msgDict["msg"] == "projectorOff":
            self._projectorOff()


    def _projectorOn(self):
            self._sendCommand("power")
            self.controller.state.projectorOn = True

    def _projectorOff(self):
            self._sendCommand("power")
            self._sendCommand("power")
            self.controller.state.projectorOn = False

    def _sendCommand(self, command):
        remote = self.config.get("projector", "remote")
        self.sendTo("irtrans", {"msg": "irsend", "remote": remote, "command": command})


