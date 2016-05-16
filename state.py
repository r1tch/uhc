#!/usr/bin/env python3

class State:
    """Common object accessible by all services, to store current states"""
    def __init__(self):
        self.atHome = True   # we're home if alarm system is unarmed
        self.asleep = False  # detected based on movements around the house

