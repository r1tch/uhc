#!/usr/bin/env python3

import json

import zwavenodes

class UhcJsonEncoder(json.JSONEncoder):
    """Encodes UHC data structures to JSON"""
    def default(self, obj):
        if isinstance(o, zwavenodes.ZWaveNodes.ZWaveNode):
            return { "id": o.id, "name": o.name, "type": o.type }

        if isinstance(o, zwavenodes.ZWaveNodes):
            return o.allNodes()

        return super().default(o)

