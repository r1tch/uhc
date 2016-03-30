#!/usr/bin/env python3

class ZWaveNodes:
    class ZWaveNode:
        def __init__(self, id, name, type):
            self.id = int(id)
            self.name = name
            self.type = type
            self.level = 0              # later we might introduce subclasses, for now this is enough

    def __init__(self):
        self._byName = {}
        self._byId = {}

    def add(self, node):
        self._byId[node.id] = node
        self._byName[node.name] = node

    def byId(self, id):
        return self._byId[int(id)]

    def byName(self, name):
        return self._byName[name]

    def typeOf(self, id):
        return self._byId[int(id)].type

    def levelOf(self, id):
        return self._byId[int(id)].level

    def allIds(self):
        return self._byId.keys()

    def allNodes(self):
        return self._byId.values()

    def __len__(self):
        return len(self._byId)


