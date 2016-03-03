#!/usr/bin/env python3

import asyncio
import logging

import tcpserver

class Controller:
    def run(self):
        logging.info("Controller startup")
        eventloop = asyncio.get_event_loop()
        eventloop.set_debug(True)
        eventloop.call_soon(Controller.w, self)

        self.tcpserver = tcpserver.TcpServer(eventloop)
        eventloop.run_forever()

    def w(self):
        print("Just testing")
        logging.warning("warn2")
        logging.info("hi2")
