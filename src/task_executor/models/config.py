# config.py
# version 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-09-29
# Last Modified: 2025-09-29

class Config:
    def __init__(self, config_dict: dict):

        if not "missions" in config_dict and not type(config_dict["missions"]) is dict[str, str]:
            raise ValueError("Missing 'missions' in configuration")

        if not "takeoff" in config_dict["missions"]:
            raise ValueError("Missing 'takeoff' in configuration")

        if not "land" in config_dict["missions"]:
            raise ValueError("Missing 'land' in configuration")

        if not "controller" in config_dict:
            raise ValueError("Missing 'controller' in configuration")
        
        self.missions = config_dict["missions"]
        self.controller = config_dict["controller"]


