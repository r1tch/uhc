#!/usr/bin/env python3

import asyncio
import ipaddress
import logging
import sys


class TcpServer:
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
            else:
                logging.info('TcpServer: remote connection from {} - CLOSING'.format(peername))
                transport.abort()

        def data_received(self, data):
            message = data.decode()
            print('Data received: {!r}'.format(message))
            self.tcpServer.testCallback(message)

            if message == "exit\n":
                sys.exit()

            self.transport.write("Thank you\n".encode())

        def is_local(addressStr):
            if ':' in addressStr:
                address = ipaddress.IPv6Address(addressStr)
            elif '.' in addressStr:
                address = ipaddress.IPv4Address(addressStr)

            return address.is_private or address.is_local or address.is_link_local

    def createRemoteProtocol(self):
        return TcpServer.RemoteProtocol(self)

    def __init__(self, config, eventloop):
        self.eventloop = eventloop
        coroutine = self.eventloop.create_server(self.createRemoteProtocol, port=config.getint("remote", "port"))
        self.eventloop.run_until_complete(coroutine)

    def testCallback(self, msg):
        print("testcallback: " + msg)
