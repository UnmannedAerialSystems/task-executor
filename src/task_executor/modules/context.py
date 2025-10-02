# src/task_executor/modules/context.py
# version: 1.0.1
# Author: Theodore Tasman
# Creation Date: 2025-09-30
# Last Modified: 2025-10-01

from task_executor.models.context_config import ContextConfig
from task_executor.modules.queue import Queue

from task_executor.utils.zmq_broker import ZMQBroker

from MAVez.flight_controller import FlightController

from logging import Logger
import asyncio

class Context:
    """
    Context class to hold configuration and state information.
    """

    def __init__(self, config: ContextConfig, logger: Logger | None = None):
        self.missions = config.missions
        self.zmq = config.zmq

        self.controller = FlightController(
            logger=logger,
            zmq_host=config.zmq.host,
            zmq_port=config.zmq.telemetry.port,
            zmq_topic=config.zmq.telemetry.topic,
        )

        self.queue = Queue()
        self.zmq_broker = ZMQBroker(
            host=config.zmq.host,
            port=config.zmq.tasks.port
        )

        # task state
        self.task_completed_event = asyncio.Event()

        # mission state
        self.current_mission_length: int = -1
        self.current_mission_index: int = -1
        self.mission_in_progress: bool = False
        self.mission_completed: bool = False

        # queue
        self.queue = Queue()    

        self.running_task: asyncio.Task | None = None

    def reset_mission_progress(self):
        """
        Reset the mission progress state.
        """
        self.mission_in_progress = False
        self.current_mission_index = -1
        self.current_mission_length = -1
