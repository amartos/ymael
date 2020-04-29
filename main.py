#!/usr/bin/env python3


def notify_crash(log_file):
    import notify2

    notify2.init("Ymael")
    notifier = notify2.Notification("Ymael: a fatal error occured.","See logs in {}".format(log_file))
    notifier.show()
    return

def main():
    import os, platform
    import logging
    from datetime import datetime

    from ymael.core import Ymael

    if platform.system() == "Windows":
        local = os.getenv('%LOCALAPPDATA%')
        data_folder = local+"/ymael/"
    else:
        data_folder = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))+"/ymael/"

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
        Ymael(rps_folder)
    except Exception:
        logger.exception("A fatal error occurred.")
        notify_crash(log_file)
        exit(1)

    # remove empty log file
    logging.shutdown()
    if os.stat(log_file).st_size == 0:
        os.remove(log_file)

if __name__=="__main__":
    main()
