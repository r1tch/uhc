#!/usr/bin/env python3

import asyncio
import logging

from autoshade import AutoShade
from autolight import AutoLight
from irtrans import IrTrans
from kodi import Kodi
from paradox import Paradox
from tcpserver import TcpServer
from zwave.mios import ZWaveMios
from schedule import Schedule
from state import State
from sunriseset import SunRiseSet

class Controller:
    """Serves as factory, container and coordinator of Service classes"""
    def __init__(self, config):
        self.config = config
        self.services = {}
        self.state = State()

    def _createServices(self, eventloop):
        """Hardcoding a list of services - later we might add auto-detection of services present"""
        AutoShade(self, self.config, eventloop)
        AutoLight(self, self.config, eventloop)
        IrTrans(self, self.config, eventloop)
        Kodi(self, self.config, eventloop)
        Paradox(self, self.config, eventloop)
        Schedule(self, self.config, eventloop)
        SunRiseSet(self, self.config, eventloop)
        ZWaveMios(self, self.config, eventloop)
        TcpServer(self, self.config, eventloop)

    def run(self):
        logging.info("Controller startup")
        eventloop = asyncio.get_event_loop()
        # eventloop.set_debug(True)
        self._createServices(eventloop)

        eventloop.run_forever()
