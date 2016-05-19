

TODO: describe services and json comm

Drawback: "msg" part should also be unique, due to broadcast support.

TODO: fix formatting

## Example Commands

(TODO: this should be a full list of accepted msgs.)

{ "service": "zwave", "msg": "getNodes" }
{ "service": "zwave", "msg": "setLevel", "id": "13", "level": "100" }
{ "service": "zwave", "msg": "stopLevelChange", "id": "12" }
{ "service": "zwave", "msg": "setAllLights", "level": "0" }



## Example Updates

{ "fromService": "zwave", "msg": "gotNodes", "nodes": [{"id": 1, "name": "ZWave", "level": 0, "type": "ZWaveNetwork"}, {"id": 2, "name": "Scene Controller", "level": 0, "type": "ZWaveNetwork"}] }
{ "fromService": "zwave", "msg": "changedLevels", "changedLevels": {"26": 100, "19": 100, "21": 100, "22": 100} }

