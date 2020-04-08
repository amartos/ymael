# -*- coding: utf-8 -*-

import os


class FileManager:

    @classmethod
    def linux_system_init(cls):
        cls.config_folder = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))+"/ymael/"
        cls.data_folder = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))+"/ymael/"
        return cls()

    @classmethod
    def windows_system_init(cls):
        local = os.getenv('%LOCALAPPDATA%')
        cls.config_folder = local+"/ymael/config/"
        cls.data_folder = local+"/ymael/local/share/"
        return cls()

    def __init__(self):
        self.software_path = os.path.realpath(__file__).replace("ymael/files/filemanager.py", "")
        self.icons_path = self.software_path+"icons/"
        self.ymael_icon = self.icons_path+"ymael.ico"
        self.readme = self.software_path+"README.md"
        self.rps = self.data_folder+"rps/"
        self.watch_list = self.data_folder+"watch_list"
        self.charname_file = self.data_folder+"character"
        self._launch_status_check()

    def _launch_status_check(self):
        for folder in [self.config_folder,self.data_folder,self.rps]:
            if not os.path.exists(folder):
                os.mkdir(folder)
        for filename in [self.rps, self.watch_list]:
            self.check_path(filename)

    def check_path(self, path):
        if not os.path.exists(path):
            open(path,'w').close()
