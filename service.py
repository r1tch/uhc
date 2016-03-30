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
        """Should return a unique ID"""
        raise NotImplementedError

    def addTo(self, services):
        services[self.id()] = self

    def broadcast(self, event):
        """Called by subclasses upon events"""
        for listener in listeners:
            listener.event(self, event)     ## TODO listener base class? event(sourceService, event)

    def execute(self, command):
        """Execute a command, command being a dict() (convertable from JSON), retval being a dict() too (for JSON); should return immediately!"""
        raise NotImplementedError
