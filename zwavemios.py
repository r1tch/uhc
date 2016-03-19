#!/usr/bin/env python3

import logging
import requests
import threading

from zwavenodes import ZWaveNodes
from zwavemiosnodelistquery import ZWaveMiosNodelistQuery

class ZWaveMios:
    STATUS_URL=":3480/data_request?id=status&output_format=json"

    class Node:
        def __init__(self):
            pass
    
    def __init__(self, config, eventloop):
        self.config = config
        self.eventloop = eventloop
        self.zwavenodes = ZWaveNodes()
        self.nodelistquery = ZWaveMiosNodelistQuery(config, eventloop, self.gotNodes)

    def gotNodes(self, zwavenodes):
        self.zwavenodes = zwavenodes
        self.getStatus()
        # TODO notify listeners about new node list

    def getStatus(self):
        self.eventloop.run_in_executor(None, self.getStatusInThread)

    def getStatusDone(self, status):
        #print("getStatusDone onthread:" + str(threading.currentThread().ident))
        if not 'devices' in status:
            logging.error("No 'devices' in status JSON: " + str(status))
            return

        for device in status['devices']:
            self.updateDeviceStateFromJson(device)

        timeout = self.config.getint("mios", "update_frequency_secs")
        self.eventloop.call_later(timeout, self.getStatus)

    def updateDeviceStateFromJson(self, device):
        if not 'id' in device or not 'states' in device:
            logging.error("No 'id' or no 'states' in device JSON: " + str(device))
            return

        print("----Device {} ----".format(device['id']))
        self.printStatesFor(device['states'])

    def printStatesFor(self, states):
        for state in states:
            print("{} {}: {}".format(state['service'], state['variable'], state['value']))

    # Worker thread methods
    def getStatusInThread(self):
        host = self.config.get("mios", "host")
        url = "http://{}{}".format(host, ZWaveMios.STATUS_URL)
        # print("requesting " + url)
        resp = requests.get(url)
        # print("response code:" + str(resp.status_code))
        json = resp.json()
        self.eventloop.call_soon_threadsafe(self.getStatusDone, json)


