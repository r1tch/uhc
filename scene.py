#!/usr/bin/env python3

import logging

from service import Service
import time

class Scene(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        self.config = config
        self.controller = controller
        self.eventloop = eventloop
        self.sunrise = 0
        self.sunset = 0

    #@override
    def id(self):
        return "scene"
    
    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "SunRiseSet":
            self.sunrise = msgDict["sunrise"]
            self.sunset = msgDict["sunset"]
            return

        if "msg" not in msgDict or msgDict["msg"] != "selectScene" or "scene" not in msgDict:
            return

        newScene = msgDict["scene"]
        currentScene = self.controller.state.scene

        if currentScene == newScene:
            return

        if newScene not in ("cozy", "movie", "none"):
            logging.error("Scene {} unknown.".format(scene))
            return

        if newScene == "cozy":
            self._activateCozy(currentScene)
        elif newScene == "movie":
            self._activateMovie(currentScene)
        elif newScene == "none":
            self._activateNone(currentScene)
        
        self.controller.state.scene = newScene

    def _activateCozy(self, currentScene):
        if currentScene == 'movie':
            self._deactivateMovie()

        lightsToBeOn = self.config.get("scene", "cozylightsOn")
        self.sendTo("zwave", { "msg": "turnOnOnlyLights", "names": lightsToBeOn })

        for shade in self.config.get("scene", "cozyshadesDown").split(','):
            self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 0 })

        # for now, playlistid and playerid hardcoded...
        cozymusicDirectory = self.config.get("scene", "cozymusicDirectory")
        if cozymusicDirectory:
            self._sendToKodi({"method": "Playlist.Clear", "params":{"playlistid":0}})
            self._sendToKodi({"method": "Player.SetShuffle", "params":{"playerid":0, "shuffle": True}})
            self._sendToKodi({"method": "Playlist.Add", "params":{"playlistid":0, "item": {"directory": cozymusicDirectory}}})
            self._sendToKodi({"method": "Player.Open", "params": { "item": {"playlistid": 0}}})
            self._sendToKodi({"method": "Application.SetVolume", "params": {"volume": 70}})

            self.sendTo("hifi", { "msg": "hifiOn" })
            self.sendTo("hifi", { "msg": "setMediaSource" })


    def _activateMovie(self, currentScene):
        if currentScene == 'cozy':
            self._deactivateCozy()

        self.sendTo("zwave", { "msg": "setAllLights", "level": 0 })

        for shade in self.config.get("scene", "movieshadesDown").split(','):
            self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 0 })

        moviescreen = self.config.get("scene", "moviescreen")
        if moviescreen:
            self.sendTo("zwave", { "msg": "setLevel", "name": moviescreen, "level": 0 })

        self.sendTo("projector", { "msg": "projectorOn" })

        for playerid in (0, 1, 2, 3, 4):
            self._sendToKodi({"method": "Player.Stop", "params": { "playerid": playerid }})

        self._sendToKodi({"method": "Application.SetVolume", "params": {"volume": 100}})

        self.sendTo("hifi", { "msg": "hifiOn" })
        self.sendTo("hifi", { "msg": "setMediaSource" })

    def _activateNone(self, currentScene):
        if currentScene == 'movie':
            self._deactivateMovie()

        if currentScene == 'cozy':
            self._deactivateCozy()


    def _deactivateMovie(self):
        moviescreen = self.config.get("scene", "moviescreen")
        if moviescreen:
            self.sendTo("zwave", { "msg": "setLevel", "name": moviescreen, "level": 100 })
        self.sendTo("projector", { "msg": "projectorOff" })

        if self._isLight():
            for shade in self.config.get("scene", "movieshadesDown").split(','):
                self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 100 })
        if self._isDark():
            for light in self.config.get("scene", "normallightsOn").split(','):
                self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 100 })


    def _deactivateCozy(self):
        if self._isLight():
            for shade in self.config.get("scene", "cozyshadesDown").split(','):
                self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 100 })
            for light in self.config.get("scene", "cozylightsOn").split(','):
                self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 0 })
        if self._isDark():
            for light in self.config.get("scene", "normallightsOn").split(','):
                self.sendTo("zwave", { "msg": "setLevel", "name": shade, "level": 100 })

        cozymusicDirectory = self.config.get("scene", "cozymusicDirectory")
        if cozymusicDirectory:
            self._sendToKodi({"method": "Player.SetShuffle", "params":{"playerid":0, "shuffle": False}})
            self._sendToKodi({"method": "Player.PlayPause", "params": {"playerid": 0}})


    def _isDark(self, when = 0):
        if not when:
            when = time.time()
        return when < self.sunrise or when > self.sunset

    def _isLight(self, when = 0):
        if not when:
            when = time.time()
        return not self._isDark(when)

    def _sendToKodi(self, msgDict):
        msgDict["jsonrpc"] = "2.0"
        self.sendTo("kodi", msgDict)




