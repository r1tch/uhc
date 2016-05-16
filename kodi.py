#!/usr/bin/env python3

import asyncio
import config
import json
import logging

from service import Service
from uhcjson import UhcJsonEncoder, UhcJsonChunkParser

# Kodi JSON RPC forwarder

# Translate tcpserver's connection to jsonrpc ID
# For later: we could get smarter and do the polling only here, to avoid duplications.
# ...but hey, we have a Gbit network :)

class Kodi(Service):
    class ClientProtocol(asyncio.Protocol):
        def __init__(self, kodi):
            self.kodi = kodi
            self.chunkParser = UhcJsonChunkParser(jsonReceiver=self)

        def connection_made(self, transport):
            self.transport = transport
            peername = self.transport.get_extra_info('peername')
            self.chunkParser.peername = peername
            logging.info('Kodi: new connection to {}'.format(peername))
            self.kodi._onConnectionMade(self)

        def connection_lost(self, exception):
            peername = self.transport.get_extra_info('peername')
            logging.info('Kodi: connection lost from {}'.format(peername))
            self.kodi._onConnectionLost()

        def data_received(self, data):
            self.chunkParser.parseBytes(data)

        def write(self, msgStr):
            self.transport.write(msgStr.encode())

        # UhcJsonChunkParser callback
        def jsonReceived(self, jsonData):
            self.kodi.jsonReceived(jsonData)

        # UhcJsonChunkParser callback
        def jsonError(self):
            self.transport.close()

    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.eventloop = eventloop
        self.connection = None

        self.host = config.get("kodi", "host")
        self.port = config.getint("kodi", "port")
        self.reconnectTimeout = config.getint("kodi", "reconnectTimeout")
        self._initiateConnection()

    #@override
    def id(self):
        return "kodi"

    #@override
    def msg(self, fromService, msgDict):
        if "service" not in msgDict or msgDict["service"] != self.id():      # do not interpret broadcasts; just forward directly sent msgs
            return

        msgDict["jsonrpc"] = "2.0"
        if not self.connection:
            logging.error("Kodi: not sending msg while not connected")
            return

        if "connection" in msgDict:
            del msgDict["connection"]       # only element not JSON serializable; jsonrpc uses "id" property to ID connections
        jsonStr = UhcJsonEncoder().encode(msgDict)
        logging.debug("Sending {}".format(jsonStr))
        self.connection.write(jsonStr)

    def _initiateConnection(self):
        coroutine = self.eventloop.create_connection(lambda: Kodi.ClientProtocol(self), self.host, self.port)
        asyncio.ensure_future(coroutine)

    def _onConnectionMade(self, connection):
        if self.connection:
            logging.error("Kodi: connected while another connection was up; using new one")

        self.connection = connection

    def _onConnectionLost(self):
        self.connection = None
        self._delayedReconnect()

    def _delayedReconnect(self):
        self.eventloop.call_later(self.reconnectTimeout, self._initiateConnection)


    def jsonReceived(self, jsonData):
        logging.debug("Received: {}".format(jsonData))
        self.sendTo("tcpserver", jsonData)



if __name__ == '__main__':
    jsonData = json.loads('{"t":1}{"') # extra data
    #jsonData = json.loads('{"test": 1') # incomplete obj 1
    # jsonData = json.loads('{"test": ') # incomplete obj 2
    #jsonData = json.loads('{"test') # incomplete prop
    #jsonData = json.loads('{"test": "asdf') # incomplete prop
