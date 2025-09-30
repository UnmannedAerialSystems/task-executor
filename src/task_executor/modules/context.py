# src/task_executor/modules/context.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-09-30
# Last Modified: 2025-09-30

from MAVez.flight_controller import FlightController

from logging import Logger

class Context:

    def __init__(self, config_dict: dict, logger: Logger | None = None):

        # mission validation
        if not "missions" in config_dict or not isinstance(config_dict["missions"], dict):
            raise ValueError("Missing or invalid 'missions' in configuration")

        if not "takeoff" in config_dict["missions"] or not isinstance(config_dict["missions"]["takeoff"], str):
            raise ValueError("Missing or invalid 'takeoff' in configuration")

        if not "land" in config_dict["missions"] or not isinstance(config_dict["missions"]["land"], str):
            raise ValueError("Missing or invalid 'land' in configuration")
        
        self.missions: dict[str, str] = config_dict["missions"]
        # end mission validation

        # zmq validation
        if not "zmq" in config_dict or not isinstance(config_dict["zmq"], dict):
            raise ValueError("Missing or invalid 'zmq' in configuration")
        
        if not "host" in config_dict["zmq"] or not isinstance(config_dict["zmq"]["host"], str):
            raise ValueError("Missing or invalid 'host' in 'zmq' configuration")
        self.zmq_host: str = config_dict["zmq"]["host"]

        if not "port" in config_dict["zmq"] or not isinstance(config_dict["zmq"]["port"], int):
            raise ValueError("Missing or invalid 'port' in 'zmq' configuration")
        self.zmq_port: int = config_dict["zmq"]["port"]
        
        if not "topic" in config_dict["zmq"] or not isinstance(config_dict["zmq"]["topic"], str):
            raise ValueError("Missing or invalid 'topic' in 'zmq' configuration")
        self.zmq_topic: str = config_dict["zmq"]["topic"]
        # end zmq validation


        self.controller = FlightController(
            logger=logger, 
            zmq_host=str(self.zmq_host), 
            zmq_port=int(self.zmq_port), 
            zmq_topic=str(self.zmq_topic)
        )