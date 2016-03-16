#!/usr/bin/env python3

import requests
import threading

import zwavenodes

class ZWaveMios:
    STATUS_URL=":3480/data_request?id=status&output_format=json"

    class Node:
        def __init__(self):
            pass
    
    def __init__(self, config, eventloop):
        self.config = config
        self.eventloop = eventloop
        self.zwavenodes = zwavenodes.ZWaveNodes()
        self.getStatus()

    def getStatusWorker(self):
        host = self.config.get("mios", "host")
        url = "http://{}{}".format(host, ZWaveMios.STATUS_URL)
        print("requesting " + url)
        resp = requests.get(url)
        print("response code:" + str(resp.status_code))
        json = resp.json()
        print("Got: " + str(json))
        # self.eventloop.call_soon_threadsafe(....) -- call back on main thread, won't need sync!!
        print("onthread:" + str(threading.currentThread().ident))

    def getStatus(self):
        self.eventloop.run_in_executor(None, self.getStatusWorker)


