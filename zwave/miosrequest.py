#!/usr/bin/env python3

import logging
import requests

class ZWaveMiosRequest:
    LUA_ACTION_URL=":3480/data_request?id=action&output_format=json"

    def __init__(self, config, eventloop, statusCallback):
        self.config = config
        self.eventloop = eventloop
        self.statusCallback = statusCallback # TODO immediate callback on changed levels!
        self.zwavenodes = None

    def setNodes(self, zwavenodes):
        self.zwavenodes = zwavenodes

    def setLevelByName(self, name, level):
        node = self.zwavenodes.byName(name)
        self.setLevel(node.id, level)

    def setLevel(self, id, level):
        """Sets level for node with given id; level should be 0-100"""
        # http://ip_address:3480/data_request?id=action&output_format=xml&DeviceNum=6&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=1
        # http://ip_address:3480/data_request?id=lu_action&output_format=json&DeviceNum=7&serviceId=urn:upnp-org:serviceId:Dimming1&action=SetLoadLevelTarget&newLoadLevelTarget=30
        # Wiki contains both id=action and id=lu_action. Both work fine.
        # services and actions defined in: http://wiki.micasaverde.com/index.php/Luup_UPnP_Variables_and_Actions
        # also see user_data.txt, <Command> and <Parameters> define what we can send

        logging.debug("setLevel for {}, level:{}".format(id, level))
        try:
            node = self.zwavenodes.byId(id)
            value = level
            if node.type == "BinaryLight":
                luaService, action, variable = ("SwitchPower1", "SetTarget", "newTargetValue")
                if level < 50:
                    level = 0
                    value = 0
                elif level >=50:
                    level = 100
                    value = 1
            elif node.type == "WindowCovering" or node.type == "DimmableLight":
                # assuming that dimming will work for shades too...
                luaService, action, variable = ("Dimming1", "SetLoadLevelTarget", "newLoadlevelTarget")
            else:
                logging.error("setLevel requested for {} ({}) of type {}".format(id, node.name, node.type))
                return
            self.eventloop.run_in_executor(None, self._requestLuaAction, id, luaService, action, variable, value)
            self.statusCallback({id: level})
        except KeyError as e:
            logging.error("Node {} probably not found: {}".format(id, e))


    def stopLevelChange(self, id):
        luaService = "WindowCovering1"
        action = "Stop"
        self.eventloop.run_in_executor(None, self._requestLuaAction, id, luaService, action)

    def setAllLights(self, level):
        for node in self.zwavenodes.allNodes():
            if node.type in ("BinaryLight", "DimmableLight"):
                self.setLevel(node.id, level)

    def turnOnOnlyLights(self, lightsToBeOn):
        for node in self.zwavenodes.allNodes():
            if node.type not in ("BinaryLight", "DimmableLight"):
                continue

            if node.name in lightsToBeOn:
                self.setLevel(node.id, 100)
            else:
                self.setLevel(node.id, 0)

    # Worker thread methods
    def _requestLuaAction(self, id, luaService, action, variable="", value=0):
        host = self.config.get("mios", "host")
        params = "&DeviceNum={}&serviceId=urn:upnp-org:serviceId:{}&action={}".format(id, luaService, action)
        if variable:
            params += "&{}={}".format(variable, value)
        url = "http://{}{}{}".format(host, ZWaveMiosRequest.LUA_ACTION_URL, params)
        resp = requests.get(url)
        logging.info("action response ({}): {}".format(resp.status_code, resp.text))


