#!/usr/bin/env python3

import asyncio
import ipaddress
import logging
import sys

from service import Service
from uhcjson import UhcJsonEncoder

class TcpServer(Service):
    class RemoteProtocol(asyncio.Protocol):
        def __init__(self, tcpServer):
            self.tcpServer = tcpServer
            print("New RemoteProtocol created")

        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            print('Connection from {}'.format(peername))
            self.transport = transport
            if TcpServer.RemoteProtocol.is_local(peername[0]):
                logging.info('TcpServer: local connection from {}'.format(peername))
                self.tcpServer._newConnection(self)
            else:
                logging.info('TcpServer: remote connection from {} - CLOSING'.format(peername))
                transport.abort()

        def connection_lost(self, exception):
            peername = self.transport.get_extra_info('peername')
            logging.info('TcpServer: connection lost from {}'.format(peername))
            self.tcpServer.connections.remove(self)

        def data_received(self, data):
            message = data.decode()
            print('Data received: {!r}'.format(message))
            self.tcpServer._testCallback(message)

            if message == "exit\n":
                sys.exit()

            self.transport.write("Thank you\n".encode())

        def is_local(addressStr):
            if ':' in addressStr:
                address = ipaddress.IPv6Address(addressStr)
            elif '.' in addressStr:
                address = ipaddress.IPv4Address(addressStr)

            return address.is_private or address.is_local or address.is_link_local

    def __init__(self, container, config, eventloop):
        super().__init__(container)
        self.eventloop = eventloop
        self.connections = set()
        coroutine = self.eventloop.create_server(self._createRemoteProtocol, port=config.getint("remote", "port"))
        self.eventloop.run_until_complete(coroutine)
   
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
        
        jsonStr = UhcJsonEncoder().encode(msgDict)

        if targetConnection:
            self._writeTo(targetConnection, jsonStr)
        else:
            for connection in self.connections:
                self._writeTo(connection, jsonStr)
        
    def _writeTo(self, connection, jsonStr):
        connection.transport.write((jsonStr + "\n").encode())

    def _createRemoteProtocol(self):
        return TcpServer.RemoteProtocol(self)

    def _newConnection(self, connection):
        self.connections.add(connection)
        msgDict = { "msg": "getNodes", "connection": connection }
        self.sendTo("zwave", msgDict)

    def _testCallback(self, msg):
        print("testcallback: " + msg)
