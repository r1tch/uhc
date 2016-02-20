#!/usr/bin/env python
import logging
import os

from Controller import Controller

if __name__ == '__main__':
    logging.basicConfig(filename=os.getenv("HOME") + "/test.log",
                        level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Init")
    c = Controller()
    c.run()
