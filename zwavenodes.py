#!/usr/bin/env python3

class ZWaveNodes:
    class ZWaveNode:
        def __init__(self, id, name, type):
            self.id = id
            self.name = name
            self.type = type

    def __init__(self):
        self._byName = {}
        self._byId = {}

    def add(self, node):
        self._byId[node.id] = node
        self._byName[node.name] = node

    def byId(self, id):
        return self._byId[id]

    def byName(self, name):
        return self._byName[name]

    def allNodes(self):
        return self._byId.values()

    def byType(self, type):
        # TODO reduce _byId.values() by type & lambda
        # TODO needed at all??
        pass

