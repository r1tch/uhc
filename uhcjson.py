#!/usr/bin/env python3

import json
import logging

from scheduledevent import ScheduledEvent
from zwave.nodes import ZWaveNodes

class UhcJsonEncoder(json.JSONEncoder):
    """Encodes UHC data structures to JSON"""
    def default(self, obj):
        if isinstance(obj, ZWaveNodes.ZWaveNode):
            return { "id": obj.id, "name": obj.name, "type": obj.type, "level": obj.level }

        if isinstance(obj, ScheduledEvent):
            return { "id": obj.id, "fromServiceId": obj.fromServiceId, "at": obj.at, "desc": obj.desc, "deferredMsg": obj.deferredMsg }

        if isinstance(obj, ZWaveNodes):
            return obj.allNodes()

        # does not work, dict_values is unknown!?!?!
        #if isinstance(obj, dict_values):
        if obj.__class__.__name__ == "dict_values":
            return list(obj)    # thread unsafe if obj is mutable (but it's immutable!)

        if isinstance(obj, (dict, list, str, int, float, bool)):
            return obj

        return super().default(obj) # throw not JSON serializable exception

class UhcJsonChunkParser:
    def __init__(self, jsonReceiver):
        self.buf = str()
        self.jsonReceiver = jsonReceiver
        self.peername = "UnknownPeer"

    def parseBytes(self, data):
        message = data.decode()
        self.buf += message
        while self._decodeObjectFromBuf():
            pass

    # retval == if we should continue parsing after this object
    def _decodeObjectFromBuf(self):
        try:
            jsonData = json.loads(self.buf)
        except json.decoder.JSONDecodeError as e:
            if e.msg.startswith("Expecting "):         # keep the buffer, more might come
                return False
            if e.msg.startswith("Unterminated "):      # keep the buffer, more might come
                return False
            if e.msg.startswith("Extra data: "):       # we have a full object, let's retry parsing it!
                remainder = self.buf[e.pos:]
                self.buf = self.buf[:e.pos]
                self._decodeObjectFromBuf()
                self.buf = remainder
                return True
            logging.error('unhandled JSONDecodeError: {}'.format(e))
            raise e
        except ValueError as e:
            logging.error("irrecoverable JSON error: {}, exception: {}".format(message, e))
            self.jsonReceiver.jsonError()
            return False

        self.buf = str()
        logging.info("received {}: {}".format(self.peername, jsonData))
        self.jsonReceiver.jsonReceived(jsonData)

