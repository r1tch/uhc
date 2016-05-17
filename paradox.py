#!/usr/bin/env python3

import asyncio
import logging
import serial

from service import Service

ZoneClosed       = 0
ZoneOpen         = 1
PartitionStatus  = 2
BellStatus       = 3
ArmWithUser      = 29
SpecialArming    = 30
DisarmWithUser   = 31
DisarmAAWithUser = 32
AlarmCxlWithUser = 33
SpecialDisarm    = 34
ZoneAlarm        = 36
FireAlarm        = 37
ZoneAlarmRestore = 38
FireAlarmRestore = 39
SpecialAlarm     = 40
NewTrouble       = 44
TroubleRestored  = 45
SpecialEvent     = 48


SilentAlarm  =             2
BuzzerAlarm  =             3
SteadyAlarm  =             4
PulsedAlarm  =             5
Strobe       =             6
AlarmStopped =             7
SquawkOn     =             8
SquawkOff    =             9
GroundStart  =             10
DisarmPartition         =  11
ArmPartition            =  12
EntryDelayStarted       =  13
ExitDelayStarted        =  14
PreAlarmDelay           =  15
AnyPartitionStatusEvent =  99

TelephoneLine  = 0
ACFailure      = 1
BatteryFailure = 2
AuxiliaryCurrentOverload       = 3
BellCurrentOverload            = 4
BellDisconnected               = 5
ClockLoss                      = 6
FireLoopTrouble                = 7
FTCCentral1                    = 8
FTCCentral2                    = 9
FTCPager = 10
FTCVoice = 11
GSMJamming                     = 13
GSMNoService                   = 14
GSMSupervisionLost             = 15
FailToCommunicateIPReceiver1   = 16
FailToCommunicateIPReceiver2   = 17
IPModuleNoService              = 18
IPModuleSupervisionLoss        = 19
FailToCommunicateIPReceiver1IP = 20
FailToCommunicateIPReceiver2IP = 21
AnyTroubleEvent                = 99


class Paradox(Service):
    def __init__(self, controller, config, eventloop):
        super().__init__(controller)
        dev = config.get('paradox', 'device')
        self.serial = serial.Serial(dev)   # default 9600 8N1 just fits Paradox
        eventloop.add_reader(self.serial, self.readSerial)
        self.trouble = ""

        zonenamesStr = config.get('paradox', 'zonenames')
        self.zonenames = {}
        for x in zonenamesStr.split(','):
            zoneid,name = x.split(':')
            self.zonenames[int(zoneid)] = name

    #@override
    def id(self):
        return "paradox"

    #@override
    def msg(self, fromService, msgDict):
        if msgDict["msg"] == "newConnection" and self.trouble:
            self.sendTo("tcpserver", {"msg": "NewTrouble", "troubleStr": troubleStr, "id": msgDict["id"]})

    def readSerial(self):
        chars_in_buffer = self.serial.inWaiting()
        while chars_in_buffer >= 37:    # we have fixed-length msgs
            msg = self.serial.read(37)
            self._processMessage(msg)
            chars_in_buffer = self.serial.inWaiting()

    def _processMessage(self, msg):
        if not self._isChecksumCorrect(msg):
            logging.error('Bad checksum on {}'.format(msg))
            return

        if self._eventGroup(msg) == ZoneClosed:
            zoneid = self._eventSubgroup(msg)
            zonename = self._getZonename(zoneid)
            logging.debug("ZoneClosed: {} - {}".format(zoneid, zonename))
            self.broadcast({"msg": "ZoneClosed", "zoneid": zoneid, "zonename": zonename})
        
        elif self._eventGroup(msg) == ZoneOpen:
            zoneid = self._eventSubgroup(msg)
            zonename = self._getZonename(zoneid)
            logging.debug("ZoneOpen: {} - {}".format(zoneid, zonename))
            self.broadcast({"msg": "ZoneOpen", "zoneid": zoneid, "zonename": zonename})
        
        elif self._eventGroup(msg) == PartitionStatus:           # only handling the two interesting ones
            if self._eventSubgroup(msg) == EntryDelayStarted:
                logging.debug("EntryDelayStarted")
                self.broadcast({"msg": "EntryDelayStarted"})

            elif self._eventSubgroup(msg) == ExitDelayStarted:
                logging.debug("ExitDelayStarted")
                self.broadcast({"msg": "ExitDelayStarted"})

        elif self._eventGroup(msg) == BellStatus:
            logging.debug("BellStatus:{}".format(self._eventSubgroup(msg)))
        
        elif self._eventGroup(msg) == ArmWithUser:
            self.controller.state.atHome = False
            logging.debug("ArmWithUser:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Armed", "user": self._eventSubgroup(msg)})
        
        elif self._eventGroup(msg) == DisarmWithUser:
            self.controller.state.atHome = True
            logging.debug("DisarmWithUser:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Disarmed", "user": self._eventSubgroup(msg)})
        
        elif self._eventGroup(msg) == DisarmAAWithUser:
            self.controller.state.atHome = True
            logging.debug("DisarmAAWithUser:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Disarmed", "user": self._eventSubgroup(msg)})
        
        elif self._eventGroup(msg) == AlarmCxlWithUser:
            self.controller.state.atHome = True
            logging.debug("AlarmCxlWithUser:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Disarmed", "user": self._eventSubgroup(msg)})
        
        elif self._eventGroup(msg) == SpecialArming:
            self.controller.state.atHome = False
            logging.debug("SpecialArming:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Armed", "user": self._eventSubgroup(msg)})
        
        elif self._eventGroup(msg) == SpecialDisarm:
            self.controller.state.atHome = True
            logging.debug("SpecialDisarm:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Disarmed", "user": self._eventSubgroup(msg)})
        
        elif self._eventGroup(msg) == SpecialAlarm:
            logging.debug("SpecialAlarm:{}".format(self._eventSubgroup(msg)))
            self.broadcast({"msg": "Disarmed", "user": self._eventSubgroup(msg)}) # ??
        
        elif self._eventGroup(msg) == NewTrouble:
            troubleStr = _troubleToStr(self._eventSubgroup(msg))
            self.trouble = troubleStr
            logging.debug("NewTrouble:{}".format(troubleStr))
            self.broadcast({"msg": "NewTrouble", "troubleStr": troubleStr})
        
        elif self._eventGroup(msg) == TroubleRestored:
            troubleStr = _troubleToStr(self._eventSubgroup(msg))
            self.trouble = ""
            logging.debug("TroubleRestored:{}".format(troubleStr))
            self.broadcast({"msg": "TroubleRestored", "troubleStr": troubleStr})
        
        elif self._eventGroup(msg) == SpecialEvent:
            if self._eventSubgroup(msg) == 1:
                logging.debug("SpecialEvent: Test")
            else:
                logging.debug("SpecialEvent:{}".format(self._eventSubgroup(msg)))
        
    def _eventGroup(self, msg):
        return msg[7]

    def _eventSubgroup(self, msg):
        return msg[8]

    def _isChecksumCorrect(self, msg):
        sum = 0
        for b in msg[:-1]:      # last character is the chksum itself
            sum += b
        sum &= 0xff

        checksumMatches = (sum == msg[36])
        if not checksumMatches:
            print("mismatch, final sum: {}, in msg: {}".format(sum, msg[36]))
        return checksumMatches

    def _getZonename(self, zoneId):
        if zoneId in self.zonenames:
            return self.zonenames[zoneId]

        return "???"




