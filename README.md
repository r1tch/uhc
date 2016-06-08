# Universal Home Controller

## Introduction

**uhc** is the backend for a simple home automation system, providing an easy-to-use JSON API.


## Structure

Each function is self-contained in an independent `Service` class, which all
use dictionary-based messages for communication. Luckily these translate well
into JSON, so it's all exported by `tcpserver.py`. 

Minimum requirement for a message is to have "msg" key, which should be unique
all over the app - to enable broadcasts sent to all services.


## Example Commands

(TODO: should really cover all types of accepted msgs.)

{ "service": "zwave", "msg": "getNodes" }
{ "service": "zwave", "msg": "setLevel", "id": "13", "level": "100" }
{ "service": "zwave", "msg": "stopLevelChange", "id": "12" }
{ "service": "zwave", "msg": "setAllLights", "level": "0" }

- testing kodi comm:
 {"service": "kodi", "jsonrpc": "2.0", "method": "Playlist.GetPlaylists"}

- get scheduled events:
 {"msg": "getScheduledEvents", "service": "schedule"}

- start flashAlarm:
 {"msg": "initiateFlashAlarm", "service": "autolight"}

- stop flashAlarm:
 {"msg": "stopFlashAlarm", "service": "autolight"}

- test entry/disarm:
 {"msg": "Armed", "service": "autolight"}
 {"msg": "Armed", "service": "autoshade"}
 {"msg": "Disarmed", "service": "autoshade"}
 {"msg": "EntryDelayStarted", "service": "autolight"}

- test setLevel:
 { "msg": "setLevel", "name": "Eloszoba", "level": 0, "service": "zwave" }
 { "msg": "setLevel", "name": "NappaliUtcaRedony", "level": 0, "service": "zwave" }

- test ir:
 { "msg": "irsend", "remote": "avr", "command": "off", "service": "irtrans" }
 { "msg": "irsend", "remote": "avr", "command": "on", "service": "irtrans" }

- projector:
 { "msg": "projectorOn", "service": "projector" }
 { "msg": "projectorOff", "service": "projector" }

- test hifi:
 { "msg": "hifiOn", "service": "hifi" }
 { "msg": "hifiOff", "service": "hifi" }
 { "msg": "setMediaSource", "service": "hifi" }

- test AC controls:
 { "msg": "acTestOn", "service": "airconditioner" }
 { "msg": "acTestOff", "service": "airconditioner" }
 { "msg": "acOn", "service": "airconditioner" }
 { "msg": "acOff", "service": "airconditioner" }
 { "msg": "acMode", "setTo": "NANA24", "service": "airconditioner" }

## Example Updates Sent to Remote Client

  {"msg": "gotNodes", "fromService": "zwave", "nodes": [{"id": 1, "level": 0, "name": "ZWave", "type": "ZWaveNetwork"}, {"id": 2, "level": 0, "name": "_Scene Controller", "type": "SceneController"}, {"id": 4, "level": 0, "name": "NappaliEbedlo", "type": "BinaryLight"}, {"id": 5, "level": 0, "name": "NappaliKanape", "type": "BinaryLight"}, {"id": 6, "level": 100, "name": "Konyha", "type": "BinaryLight"}, {"id": 7, "level": 0, "name": "Dolgozo", "type": "BinaryLight"}, {"id": 8, "level": 0, "name": "Eloszoba", "type": "BinaryLight"}, {"id": 11, "level": 0, "name": "Furdonagy", "type": "BinaryLight"}, {"id": 12, "level": 0, "name": "Furdokad", "type": "DimmableLight"}, {"id": 13, "level": 0, "name": "Halo", "type": "BinaryLight"}, {"id": 14, "level": 100, "name": "HaloRedony", "type": "WindowCovering"}, {"id": 15, "level": 100, "name": "DolgozoRedony", "type": "WindowCovering"}, {"id": 16, "level": 0, "name": "LiloRedony", "type": "WindowCovering"}, {"id": 18, "level": 0, "name": "KonyhaRedony", "type": "WindowCovering"}, {"id": 19, "level": 100, "name": "NappaliUtcaRedony", "type": "WindowCovering"}, {"id": 20, "level": 0, "name": "NappaliErkelyRedony", "type": "WindowCovering"}, {"id": 21, "level": 100, "name": "NappaliKertRedony", "type": "WindowCovering"}, {"id": 22, "level": 100, "name": "NappaliOldalRedony", "type": "WindowCovering"}, {"id": 23, "level": 0, "name": "ErkelyLampa", "type": "BinaryLight"}, {"id": 24, "level": 0, "name": "ZTH100 Controller", "type": "SceneController"}, {"id": 25, "level": 0, "name": "Lilo", "type": "DimmableLight"}, {"id": 26, "level": 100, "name": "Vaszon", "type": "WindowCovering"}]}
{"changedLevels": {"6": 0}, "msg": "changedLevels", "fromService": "zwave"}


