#!/usr/bin/env python3

import logging
import requests

class ZWaveMiosStatusUpdate:
    STATUS_URL=":3480/data_request?id=status&output_format=json"

    def __init__(self, config, eventloop, statusCallback):
        self.config = config
        self.eventloop = eventloop
        self.statusCallback = statusCallback

    def startUpdates(self):
        self.eventloop.run_in_executor(None, self.getStatusInThread)

    def getStatusDone(self, status):
        #print("getStatusDone onthread:" + str(threading.currentThread().ident))
        if not 'devices' in status:
            logging.error("No 'devices' in status JSON: " + str(status))
            return

        newlevels = {}
        for device in status['devices']:
            self.updateDeviceStateFromJson(device, newlevels)

        self.statusCallback(newlevels)

        timeout = self.config.getint("mios", "update_frequency_secs")
        self.eventloop.call_later(timeout, self.startUpdates)

    def updateDeviceStateFromJson(self, device, newlevels):
        if not 'id' in device or not 'states' in device:
            logging.error("No 'id' or no 'states' in device JSON: " + str(device))
            return

        id = device['id']
        states = device['states']
        for state in states:
            service = str(state['service'])
            variable = state['variable']
            value = state['value']
            if service.endswith("SwitchPower1") and variable == "Status":
                newlevels[id] = int(value) * 100
                return      # TODO to override LoadLevelStatus which returns bogus 255 for binary switches
            elif service.endswith("Dimming1") and variable == "LoadLevelStatus":
                newlevels[id] = int(value)

        #self.printStates(id, states)

    def printStates(self, states):
        print("----Device {} ----".format(id))
        for state in states:
            print("{} {}: {}".format(state['service'], state['variable'], state['value']))

    # Worker thread methods
    def getStatusInThread(self):
        host = self.config.get("mios", "host")
        url = "http://{}{}".format(host, ZWaveMiosStatusUpdate.STATUS_URL)
        # print("requesting " + url)
        resp = requests.get(url)
        # print("response code:" + str(resp.status_code))
        json = resp.json()
        self.eventloop.call_soon_threadsafe(self.getStatusDone, json)

