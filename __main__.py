#!/usr/bin/env python3

import logging
import os
import sys
import time
import traceback

from controller import Controller
import config

if __name__ == '__main__':

    uhc_local_dir = os.path.expanduser("~/.uhc")
    try:
        os.mkdir(uhc_local_dir)
    except FileExistsError:
        pass

    config = config.Config(uhc_local_dir)

    logging.basicConfig(filename=uhc_local_dir + "/uhc.log",
                        level=config.getint("logging", "level"),
                        format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("--------- Init ---------")
    c = Controller(config)

    firstrun = True
    while True :
        try:
            if not firstrun:
                time.sleep(30)
            firstrun = False
            c.run()
        except KeyboardInterrupt:
            logging.info("Exiting after KeyboardInterrupt")
            sys.exit()
        except SystemExit:
            logging.info("Exiting after sys.exit()")
            sys.exit()
        except:
            logging.error(traceback.format_exc())
            print(traceback.format_exc())
            logging.error("Unexpected error, waiting and restarting...")
            print("Unexpected error, waiting and restarting...")
            #logging.error("Unexpected error", sys.exc_info()[0])
            #print("Unexpected error" + sys.exc_info()[0], file = sys.stderr)

