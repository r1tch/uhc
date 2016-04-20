#!/usr/bin/env python3

import logging
import os
import sys
import time
import traceback

from controller import Controller
import config

def initLog(log_file, log_level):

    # disable http request info logs:
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    log_format = '%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    try:
        logging.basicConfig(filename=log_file,
                            level=log_level,
                            format=log_format,
                            datefmt=log_datefmt)
    except OSError:  # we prepare for read-only filesystem here, fall back to console:
        logging.basicConfig(stream=sys.stdout,
                            level=log_level,
                            format=log_format,
                            datefmt=log_datefmt)



if __name__ == '__main__':

    uhc_local_dir = os.path.expanduser("~/.uhc")
    try:
        os.mkdir(uhc_local_dir)
    except FileExistsError:
        pass

    config = config.Config(uhc_local_dir)

    log_file = uhc_local_dir + "/uhc.log"
    log_level = config.getint("logging", "level")
    initLog(log_file, log_level)

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

