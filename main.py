#!/usr/bin/env python3

import logging
import os, sys, platform
import notify2
from datetime import datetime

from ymael import CommandLine


def notify_crash(log_file):
    notify2.init("Ymael")
    notifier = notify2.Notification("Ymael: a fatal error occured.","See logs in {}".format(log_file))
    notifier.show()
    return

def main():
    if platform.system() == "Windows":
        local = os.getenv('%LOCALAPPDATA%')
        data_folder = local+"/ymael/"
    else:
        data_folder = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))+"/ymael/"

    login_file = data_folder+"default_login"
    logs_folder = data_folder+"/logs/"
    rps_folder = data_folder+"rps/"
    for folder in [data_folder,rps_folder,logs_folder]:
        if not os.path.exists(folder):
            os.mkdir(folder)

    now = datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S")
    log_file = logs_folder+now
    str_format = "[%(asctime)s] %(name)s (%(levelname)s): %(message)s"
    logging.basicConfig(filename=log_file, level=logging.WARNING, format=str_format)
    logger = logging.getLogger(__name__)

    try:
        CommandLine(rps_folder, login_file, clean_logs)
    except Exception:
        logger.exception("A fatal error occurred.")
        if "-g" in sys.argv:
            notify_crash(log_file)
        sys.exit(1)

def clean_logs():
    # remove empty log file
    logging.shutdown()
    log_file = logging.getLoggerClass().root.handlers[0].baseFilename
    if os.stat(log_file).st_size == 0:
        os.remove(log_file)

if __name__=="__main__":
    main()
