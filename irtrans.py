#!/usr/bin/env python3

import asyncio
import logging
import struct
import time

from schedule import Schedule
from service import Service

IRTRANS_PORT = 21000
COMMAND_SEND = 1

class IrTrans(Service):
    class Command:
        def __init__(self, remote, command, led):
            self.remote = remote
            self.command = command
            self.led = led

        def asBytes(self):
            # struct NetworkCommand {
            #     uint8_t  netcommand;
            #     uint8_t  mode;
            #     uint16_t timeout;
            #     int32_t  address;
            #     int32_t  protocol_version;
            #     int8_t   remote[80]; 
            #     int8_t   command[20];
            #     uint8_t  trasmit_freq;
            # };  

            address = self._getAddress()
            msgBytes = struct.pack("=BBHII80s20sB", \
                    COMMAND_SEND, 0, 0, address, 210, self.remote.encode(), self.command.encode(), 0)

            return msgBytes

        def _getAddress(self):
            if self.led == "all":
                return 3 << 17
            elif self.led == "external":
                return 2 << 17
            elif self.led == "internal":
                return 1 << 17

            logging.error("Invalid LED param in command {}: {}".format(self.command, self.led))
            return 3 << 17
            
    class ClientProtocol(asyncio.Protocol):
        def __init__(self, irtrans):
            self.irtrans = irtrans

        def connection_made(self, transport):
            self.transport = transport
            peername = self.transport.get_extra_info('peername')
            logging.info('IrTrans: new connection to {}'.format(peername))
            self.irtrans._onConnectionMade(self)

        def connection_lost(self, exception):
            peername = self.transport.get_extra_info('peername')
            logging.info('IrTrans: connection lost from {}'.format(peername))
            self.irtrans._onConnectionLost()

        def data_received(self, data):
            logging.debug("Received: {}".format(data))

        def write(self, msgBytes):
            self.transport.write(msgBytes)


    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.eventloop = eventloop

        self.queue = []
        self.clientProtocol = None
        self.queueHandle = None
        self.lastSent = 0

        self._initiateConnection()

    def _initiateConnection(self):
        host = self.config.get("irtrans", "host")
        coroutine = self.eventloop.create_connection(lambda: IrTrans.ClientProtocol(self), host, IRTRANS_PORT)
        asyncio.ensure_future(coroutine)

    def _onConnectionMade(self, clientProtocol):
        logging.debug("IrTrans connected to {}".format(clientProtocol.transport.get_extra_info('peername'))) 

        if self.clientProtocol:
            logging.error("IrTrans: connected while another connection was up; using new one")
        self.clientProtocol = clientProtocol

        self.clientProtocol.write(struct.pack("=I", 0))

    def _onConnectionLost(self):
        self.clientProtocol = None
        self._delayedReconnect()

    def _delayedReconnect(self):
        reconnectTimeout = self.config.getint("irtrans", "reconnectTimeout")
        self.eventloop.call_later(reconnectTimeout, self._initiateConnection)

    #@override
    def id(self):
        return "irtrans"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] != "irsend":
            return

        if "remote" not in msgDict or "command" not in msgDict:
            logging.error("{} send invalid irsend msg: {}".format(fromService.id(), msgDict))
            return

        led = "all"
        if "led" in msgDict:
            led = msgDict["led"]

        canQueue = True
        
        if "canQueue" in msgDict:
            canQueue = msgDict["canQueue"]

        command = IrTrans.Command(msgDict["remote"], msgDict["command"], led)

        sendDelay = self._sendDelay()

        if not sendDelay and self.clientProtocol:
            self._sendCommand(command)
        elif len(self.queue) < self.config.getint("irtrans", "maxQueueLength"):
            self._enqueueCommand(command, sendDelay)
        else:
            logging.info("IrTrans send queue full, dropping {}".format(msgDict))

    def _sendCommand(self, command):
        cmdBytes = command.asBytes()
        self.clientProtocol.write(cmdBytes)
        self.lastSent = time.time()
        logging.debug("sent {}: {}".format(len(cmdBytes), cmdBytes))

    def _sendQueuedCommand(self):
        if not self.queueHandle:
            logging.error("_sendQueuedCommand called on empty queue")
            return

        command = self.queue.pop(0)
        self._sendCommand(command)
            
        self.queueHandle = None

        if self.queue:
            sendDelay = self.config.getfloat("irtrans", "sendDelaySecs")
            self.queueHandle = self.eventloop.call_later(sendDelay, self._sendQueuedCommand)

    def _sendDelay(self):
        sendDelay = self.lastSent + self.config.getfloat("irtrans", "sendDelaySecs") - time.time()
        if sendDelay < 0:
            return 0

        return sendDelay
        
    def _enqueueCommand(self, command, sendDelay):
        self.queue.append(command)
        if not self.queueHandle:
            self.queueHandle = self.eventloop.call_later(sendDelay, self._sendQueuedCommand)

    
