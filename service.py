#!/usr/bin/env python3

class Service:
    """Base class for all services"""
    def __init__(self, container):
        self.container = container
        self.listeners = set()

    def addListener(self, listener):
        if not callable(listener.event):
            raise TypeError("listener.event should be callable")
        self.listeners.add(listener)

    def id(self):
        """Should return a possibly unique ID, for brevity, let's use 2chr strings"""
        raise NotImplementedError

    def broadcast(self, event):
        """Called by subclasses upon events"""
        for listener in listeners:
            listener.event(self, event)     ## TODO listener base class? event(sourceService, event)

    def execute(self, command):
        """Execute a command, command being a dict() (convertable from JSON)"""
        raise NotImplementedError
