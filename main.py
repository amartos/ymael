#!/usr/bin/env python3

VERSION="smart_goblin"

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
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        icon_path = exe_dir+"/share/ymael.png"
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = exe_dir+"/assets/icons/ymael.png"

    system = platform.system()
    if system == "Windows":
        local = os.getenv('%LOCALAPPDATA%')
        data_folder = local+"/ymael/"
    elif system == "Linux":
        data_folder = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))+"/ymael/"
    else:
        raise RuntimeError("OS not supported. Please report to gitea.com/amartos/ymael/issues to ask for support.")

    logs_folder = data_folder+"/logs/"
    rps_folder = data_folder+"rps/"
    for folder in [data_folder,rps_folder,logs_folder]:
        if not os.path.exists(folder):
            os.mkdir(folder)

    now = datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S")
    log_file = logs_folder+now+"_"+VERSION
    str_format = "[%(asctime)s] %(name)s (%(levelname)s): %(message)s"
    logging.basicConfig(filename=log_file, level=logging.WARNING, format=str_format)
    logger = logging.getLogger(__name__)

    try:
        CommandLine(rps_folder, icon_path, clean_logs)
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
