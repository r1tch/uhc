#!/usr/bin/env python3

import logging

from service import Service

class Airconditioner(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.controller = controller
        self.eventloop = eventloop
        self.testMode = False
        self.nextCmdHandle = None

    #@override
    def id(self):
        return "airconditioner"

    #@override
    def msg(self, fromService, msgDict):
        if "msg" not in msgDict:
            return

        if msgDict["msg"] == "acTestOn":
            self.testMode = True
            logging.info("Airconditioner test mode on.")

        if msgDict["msg"] == "acTestOff":
            self.testMode = False
            logging.info("Airconditioner test mode off.")

        if msgDict["msg"] == "acOn":
            self._sendCommand(self.controller.state.acMode)
            self.controller.state.acOn = True
        
        if msgDict["msg"] == "acOff":
            self._sendCommand("off")
            self.controller.state.acOn = False
        
        if msgDict["msg"] == "acMode" and "setTo" in msgDict:
            # no checks - bogus value will cause no problem
            # delayed invocation to prevent overload (eg when raising temp quickly)
            self.controller.state.acMode = msgDict["setTo"]

            if self.controller.state.acOn == False:     # sending the mode would turn AC on
                return

            if self.nextCmdHandle:
                self.nextCmdHandle.cancel()             # supercede previous command

            self.nextCmdHandle = self.eventloop.call_later(0.75, self._sendCommand, msgDict["setTo"])


    def _sendCommand(self, command):
        remote = self.config.get("airconditioner", "remote")
        if self.testMode:
            logging.info("Would send {} to remote {}.".format(command, remote))
        else:
            logging.info("Sending {} to remote {}.".format(command, remote))
            self.sendTo("irtrans", {"msg": "irsend", "remote": remote, "command": command})

