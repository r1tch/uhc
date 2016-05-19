#!/usr/bin/env python3

import configparser
import datetime
import logging

class Config(configparser.ConfigParser):
    def __init__(self, local_dir):
        super().__init__()
        self._set_default_values()
        self.read(local_dir + "/config.ini")
        self._sanity_checks()

    def hhmmts(self, section, key):
        """Converts a hh:mm value into UNIX timestamp"""
        try:
            hhmm = self.get(section, key).split(':')
        except:
            return 0
        
        timeDt = datetime.datetime.now().replace(hour=int(hhmm[0]), minute=int(hhmm[1]), second=0, microsecond=0)
        return timeDt.timestamp()

    def _sanity_checks(self):
        if self.getint("remote", "port") < 1 or self.getint("remote", "port") > 65535:
            logging.error("[remote] port invalid")
            self.set("remote", "port", "8888")

        if self.getfloat("autolight", "flashAlarmOnOffDelaySecs") < 1:
            logging.error("[autolight] flashAlarmOnOffDelaySecs too small")
            self.set("autolight", "flashAlarmOnOffDelaySecs", "2")

        if self.getfloat("kodi", "reconnectTimeout") < 1:
            logging.error("[kodi] reconnectTimeout too small")
            self.set("kodi", "reconnectTimeout", "5")

        if self.getfloat("mios", "update_frequency_secs") < 1:
            logging.error("[mios] update_frequency_secs too small")
            self.set("mios", "update_frequency_secs", "5")
        

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
        self.set("paradox", "zonenames", "1:Bejárat,2:Előszoba,3:Nappali,4:Nappaliüveg,5:Háló,6:Dolgozó,7:Gyerekszoba,8:Füst,9:Sziréna")

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
        self.set("autoshade", "morningopen", "NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony,DolgozoRedony")
        self.set("autoshade", "morningopenzone", "3")
        self.set("autoshade", "morningopenfrom", "6:00")
        self.set("autoshade", "morningopento", "12:00")
        self.set("autoshade", "duskclose", "NappaliUtcaRedony,KonyhaRedony,HaloRedony,DolgozoRedony")
        self.set("autoshade", "nightclose", "NappaliErkelyRedony,NappaliKertRedony,NappaliOldalRedony,NappaliUtcaRedony,KonyhaRedony,HaloRedony,LiloRedony,DolgozoRedony")
        self.set("autoshade", "nightclosetime", "3:00")

        self.add_section("autolight")
        self.set("autolight", "entrylights", "Eloszoba")
        self.set("autolight", "flashAlarmOnOffDelaySecs", "2")
        self.set("autolight", "flashAlarmDelaySecs", "15")
        self.set("autolight", "flashAlarmPreflash", "Eloszoba")
        self.set("autolight", "flashAlarmFull", "Eloszoba,NappaliEbedlo,NappaliKanape,Dolgozo")
        
        self.add_section("irtrans")
        self.set("irtrans", "host", "localhost")
        self.set("irtrans", "sendDelaySecs", "0.15")
        self.set("irtrans", "maxQueueLength", "20")
        self.set("irtrans", "reconnectTimeout", "5")

        self.add_section("hifi")
        self.set("hifi", "remote", "avr")
        self.set("hifi", "mediaSourceCommand", "vid2")



