#!/usr/bin/env python3

import asyncio
import ipaddress
import json
import logging
import sys

from service import Service
from uhcjson import UhcJsonEncoder, UhcJsonChunkParser

class TcpServer(Service):
    class RemoteProtocol(asyncio.Protocol):
        def __init__(self, tcpServer):
            self.tcpServer = tcpServer
            self.connectionid = tcpServer.get_nextid()
            self.chunkParser = UhcJsonChunkParser(jsonReceiver=self)
            print("New RemoteProtocol created")

        def connection_made(self, transport):
            self.transport = transport

            peername = self.transport.get_extra_info('peername')
            self.chunkParser.peername = peername
            print('TcpServer: connection from {}'.format(peername))
            if TcpServer.RemoteProtocol.is_local(peername[0]) or True:   ## TODO password auth!!
                logging.info('TcpServer: local connection from {}'.format(peername))
                self.tcpServer._onNewConnection(self)
            else:
                logging.info('TcpServer: remote connection from {} - CLOSING'.format(peername))
                self.transport.abort()

        def connection_lost(self, exception):
            peername = self.transport.get_extra_info('peername')
            logging.info('TcpServer: connection lost from {}'.format(peername))
            if self in self.tcpServer.connections:
                self.tcpServer.connections.remove(self)

        def data_received(self, data):
            self.chunkParser.parseBytes(data)

        def is_local(addressStr):
            if ':' in addressStr:
                address = ipaddress.IPv6Address(addressStr)
            elif '.' in addressStr:
                address = ipaddress.IPv4Address(addressStr)

            isLocal = False
            try:
                isLocal = address.is_private or address.is_local or address.is_link_local
            except AttributeError:  # if not local, is_local will not exists (??)
                pass

            return isLocal

        # UhcJsonChunkParser callback
        def jsonReceived(self, jsonData):
            self.tcpServer.jsonReceived(self, jsonData)

        # UhcJsonChunkParser callback
        def jsonError(self):
            self.transport.close()


    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        controller.state.tcpserver = self
        self.config = config
        self.eventloop = eventloop

        self.connections = set()
        self.nextid = 1

        self.eventloop.call_later(2, self._startListening)   # delayed listen, not to connect in the middle of service initialization
 
    def _startListening(self):
        coroutine = self.eventloop.create_server(lambda: TcpServer.RemoteProtocol(self), port=self.config.getint("remote", "port"))
        asyncio.ensure_future(coroutine, loop=self.eventloop)  # starts server creation in the background
        # note: sync version would be: self.eventloop.run_until_complete(coroutine)

    def get_nextid(self):
        nextid = self.nextid
        self.nextid += 1
        return nextid

    #@override
    def id(self):
        return "tcpserver"

    #@override
    def msg(self, fromService, msgDict):
        # hm, maybe we just want to send out everything verbatim
       
        msgDict["fromService"] = fromService.id()

        targetConnection = None
        if "origMsg" in msgDict:
            targetConnection = msgDict["origMsg"]["connection"]
            del msgDict["origMsg"]
       
        if "id" in msgDict and msgDict["id"] != None:
            (numId, origId) = self._getConnectionIdAndOriginalId(msgDict["id"])
            targetConnection = self._getConnectionById(numId)
            if not targetConnection:    # in the meantime our connection has closed
                return
            msgDict["id"] = origId

        jsonStr = UhcJsonEncoder().encode(msgDict)

        if targetConnection:
            self._writeTo(targetConnection, jsonStr)
        else:
            for connection in self.connections:
                self._writeTo(connection, jsonStr)

    def broadcastState(self, stateMsgDict):
        stateStr = UhcJsonEncoder().encode({ "msg": "state", "state": stateMsgDict })
        for connection in self.connections:
            self._writeTo(connection, stateStr)

    def _getConnectionIdAndOriginalId(self, jsonId):
        if not isinstance(jsonId, str):
            return (jsonId, "")

        numId = jsonId
        origId = ""
        commaPosition = jsonId.find(",")
        if commaPosition != -1:
            numId = jsonId[:commaPosition]
            origId = jsonId[commaPosition + 1:]

        numId = int(numId)

        return (numId, origId)

    def _getConnectionById(self, id):
        for connection in self.connections:
            if connection.connectionid == id:
                return connection
        return None

    def _writeTo(self, connection, jsonStr):
        connection.transport.write((jsonStr + "\n").encode())
        #peername = connection.transport.get_extra_info('peername')
        #logging.debug("sending to [{}]: {}".format(peername, jsonStr[:280]))

    def _createRemoteProtocol(self):
        return TcpServer.RemoteProtocol(self)

    def _onNewConnection(self, connection):
        self.connections.add(connection)
        msgDict = { "msg": "newConnection", "connection": connection, "id": connection.connectionid }
        self.broadcast(msgDict)

        stateStr = UhcJsonEncoder().encode({ "msg": "state", "state": self.controller.state.dictState() })
        self._writeTo(connection, stateStr)

    def jsonReceived(self, connection, jsonData):
        if "service" not in jsonData:
            logging.error("Dest service missing from JSON")
            return
        jsonData["connection"] = connection
        if "id" in jsonData:
            jsonData["id"] = str(connection.connectionid) + "," + str(jsonData["id"])
        else:
            jsonData["id"] = connection.connectionid

        self.sendTo(jsonData["service"], jsonData)

