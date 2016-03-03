#!/usr/bin/env python3

import asyncio
import logging
import sys

class TcpServer:
    class RemoteProtocol:
        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            print('Connection from {}'.format(peername))
            self.transport = transport

        def data_received(self, data):
            message = data.decode()
            print('Data received: {!r}'.format(message))

            if message == "exit\n":
                sys.exit()

            self.transport.write("Thank you".encode())

    def __init__(self, eventloop):
        self.eventloop = eventloop
        coroutine = self.eventloop.create_server(TcpServer.RemoteProtocol, port=8888)   # TODO get from config
        self.eventloop.run_until_complete(coroutine)

   



