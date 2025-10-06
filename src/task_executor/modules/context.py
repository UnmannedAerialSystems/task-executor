# src/task_executor/modules/context.py
# version: 1.0.3
# Author: Theodore Tasman
# Creation Date: 2025-09-30
# Last Modified: 2025-10-01

from task_executor.models.context_config import ContextConfig
from task_executor.models.task import Task

from task_executor.modules.queue import Queue

from MAVez.flight_controller import FlightController
from MAVez.safe_logger import configure_logging, SafeLogger

import asyncio

class Context:
    """
    Context class to hold configuration and state information.
    """

    def __init__(self, config: ContextConfig):
        self.task_missions = config.task_missions
        self.waypoint_missions = config.waypoint_missions
        self.zmq = config.zmq

        logger = configure_logging()
        self.logger = SafeLogger(logger)

        self.controller = FlightController(
            logger=logger,
            zmq_host=config.zmq.host,
            zmq_port=config.zmq.telemetry.port,
            zmq_topic=config.zmq.telemetry.topic,
        )

        # task state
        self.task_completed_event = asyncio.Event()
        self.task_completed_event.set()  # Initially set to allow first task to run

        # mission state
        self.current_mission_length: int = -1
        self.current_mission_index: int = -1
        self.mission_in_progress: bool = False
        self.mission_completed: bool = False

        # queue
        self.queue = Queue(self.logger)    

        self.task_coroutine: asyncio.Task | None = None
        self.current_task: Task | None = None

    def reset_mission_progress(self):
        """
        Reset the mission progress state.
        """
        self.mission_in_progress = False
        self.current_mission_index = -1
        self.current_mission_length = -1
