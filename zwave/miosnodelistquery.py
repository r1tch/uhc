#!/usr/bin/env python3

import logging
import requests

from .nodes import ZWaveNodes

class ZWaveMiosNodelistQuery:
    USER_DATA_URL=":3480/data_request?id=user_data&output_format=json"

    def __init__(self, config, eventloop, donecallback):
        self.config = config
        self.eventloop = eventloop
        self.donecallback = donecallback
        self.eventloop.run_in_executor(None, self.getUserDataInThread)
        self.zwavenodes = ZWaveNodes()

        if (not callable(donecallback)):
            raise TypeError("donecallback should be callable")

    def getUserDataDone(self, userdata):
        if not 'devices' in userdata:
            logging.error("No 'devices' in userdata JSON: " + str(status))
            return

        for device in userdata['devices']:
            self.addDeviceFromJson(device)

        self.donecallback(self.zwavenodes)

    def addDeviceFromJson(self, device):
        if not 'name' in device or not 'id' in device or not 'device_type' in device:
            logging.error("No 'id', 'name' or 'device' in device JSON: " + str(device))
            return

        nodetype = ZWaveMiosNodelistQuery.TranslateType(device['device_type'])
        logging.info("Got node {}: {} {} {}".format(device['id'], device['name'], device['device_type'], nodetype))

        zwavenode = ZWaveNodes.ZWaveNode(device['id'], device['name'], nodetype)
        self.zwavenodes.add(zwavenode)

    def TranslateType(miostype):
        if miostype.find("ZWaveNetwork") != -1:
            return "ZWaveNetwork"
        if miostype.find("SceneController") != -1:
            return "SceneController"
        if miostype.find("BinaryLight") != -1:
            return "BinaryLight"
        if miostype.find("DimmableLight") != -1:
            return "DimmableLight"
        if miostype.find("WindowCovering") != -1:
            return "WindowCovering"

        logging.error("Unhandled ZWave device type:" + miostype)
        return miostype

    # Worker thread methods
    def getUserDataInThread(self):
        host = self.config.get("mios", "host")
        url = "http://{}{}".format(host, ZWaveMiosNodelistQuery.USER_DATA_URL)
        resp = requests.get(url)
        json = resp.json()
        self.eventloop.call_soon_threadsafe(self.getUserDataDone, json)

