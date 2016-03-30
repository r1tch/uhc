#!/usr/bin/env python3

import json

from zwave.nodes import ZWaveNodes

class UhcJsonEncoder(json.JSONEncoder):
    """Encodes UHC data structures to JSON"""
    def default(self, obj):
        if isinstance(obj, ZWaveNodes.ZWaveNode):
            return { "id": obj.id, "name": obj.name, "type": obj.type, "level": obj.level }

        if isinstance(obj, ZWaveNodes):
            return obj.allNodes()

        # does not work, dict_values is unknown!?!?!
        #if isinstance(obj, dict_values):
        if obj.__class__.__name__ == "dict_values":
            return list(obj)    # thread unsafe if obj is mutable (but it's immutable!)

        if isinstance(obj, (dict, list, str, int, float, bool)):
            return obj

        return super().default(obj) # throw not JSON serializable exception

