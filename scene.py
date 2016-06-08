#!/usr/bin/env python3

import logging

from service import Service
import time

class Projector(Service):
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
            self._activateCozy()
        elif newScene == "movie":
            self._activateMovie()
        elif newScene == "none":
            self._activateNone()
        
        self.controller.state.scene = newScene

    def _activateCozy(self):
        #lights, shades, moviescreen, projector off, kodi (soft volume + predefined playlist, stop all players), hifiOn, hifiMediaSource
        pass

    def _activateMovie(self):
        #lights, shades, moviescreen, projector on, kodi (louder volume + stop all players), hifiOn, hifiMediaSource
        pass

    def _activateNone(self):
        # shades up/dn based on isDark
        # lights off if isDark
        # proj off, video player pause, moviescreen up
        pass

    def _isDark(self, when = 0):
        if not when:
            when = time.time()
        return when < self.sunrise or when > self.sunset

    def _isLight(self, when = 0):
        if not when:
            when = time.time()
        return not self._isDark(when)


