#!/usr/bin/env python

import logging

logger = logging.getLogger(__name__)


class Controller:
    def run(self):
        self.w()

    def w(self):
        logging.warning("warn2")
        logging.info("hi2")
