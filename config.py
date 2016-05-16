#!/usr/bin/env python3

import configparser
import datetime
import logging

class Config(configparser.ConfigParser):
    def __init__(self, local_dir):
        super().__init__()
        self._set_default_values()
        self.read(local_dir + "/config.ini")

    def hhmmts(self, section, key):
        """Converts a hh:mm value into UNIX timestamp"""
        try:
            hhmm = self.get(section, key).split(':')
        except:
            return 0
        
        timeDt = datetime.datetime.now().replace(hour=int(hhmm[0]), minute=int(hhmm[1]), second=0, microsecond=0)
        return timeDt.timestamp()

    def _set_default_values(self):
        self.add_section("logging")
        # we expect numerical values here
        # -- see logging's source (DEBUG=10, INFO=20, WARNING=30, ERROR=40)
        self.set("logging", "level", str(logging.DEBUG))     # to be replaced by WARNING after prod release

        self.add_section("remote")
        self.set("remote", "port", str(8888))

        self.add_section("mios")
        self.set("mios", "host", "10.0.1.51")
        self.set("mios", "update_frequency_secs", "3")

        self.add_section("kodi")
        self.set("kodi", "host", "10.0.1.27")   # osmc2
        self.set("kodi", "port", "9090")
        self.set("kodi", "reconnectTimeout", "5")

        self.add_section("paradox")
        self.set("paradox", "device", "/dev/ttyAMA0")  # RPi default
        self.set("paradox", "zonenames", "1:BejÃ¡rat,2:ElÅszoba,3:Nappali,4:NappaliÃveg,5:HÃ¡lÃ³,6:DolgozÃ³,7:Gyerekszoba,8:FÃ¼st,9:SzirÃ©na")

        self.add_section("location")
        self.set("location", "city", "Budapest")
        self.set("location", "country", "Hungary")
        self.set("location", "latitude", "47.48094")
        self.set("location", "longitude", "19.01664")

        self.add_section("autoshade")
        self.set("autoshade", "entryopen", "NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony,KonyhaRedony,HaloRedony,DolgozoRedony")
        self.set("autoshade", "exitclose", "NappaliErkelyRedony,NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony,KonyhaRedony,HaloRedony,DolgozoRedony,LiloRedony")
        self.set("autoshade", "floweropen", "NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony")
        self.set("autoshade", "flowerclose", "NappaliErkelyRedony,NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony,KonyhaRedony,HaloRedony,DolgozoRedony,LiloRedony")
        self.set("autoshade", "summerfloweropentime", "15:00") # keep the house cool
        self.set("autoshade", "morningopen", "NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony")
        self.set("autoshade", "morningopenzone", "3")
        self.set("autoshade", "morningopenfrom", "6:00")
        self.set("autoshade", "morningopento", "12:00")
        self.set("autoshade", "duskclose", "NappaliUtcaRedony,KonyhaRedony,HaloRedony")
        self.set("autoshade", "nightclose", "NappaliErkelyRedony,NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony,KonyhaRedony,HaloRedony,LiloRedony")
        self.set("autoshade", "nightclosetime", "3:00")

