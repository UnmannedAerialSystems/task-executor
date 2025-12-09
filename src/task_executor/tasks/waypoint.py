# src/task_executor/tasks/waypoint.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-10-02
# Organization: PSU UAS

from MAVez.mission import Mission

from uas_messenger.subscriber import Subscriber
from uas_messenger.message import Message

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

from task_executor.utils.utils import get_mission_length, is_mission_completed

class Waypoint(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)

    async def _do_execute(self) -> int:
        if not self.compiled:
            self.context.logger.critical("Waypoint task not compiled.")
            raise RuntimeError("Task must be compiled before execution.") # throw to crash coroutine
        
        if self.mission_filepath is None:
            self.context.logger.critical("Waypoint mission filepath is not available.")
            raise ValueError("Waypoint mission filepath is not available.") # throw to crash coroutine

        self.context.mission_in_progress = True
        self.context.current_mission_length = self.length
        self.context.current_task = self

        await self.mission.send_mission()
        await self.controller.set_mode("AUTO")
        self.sub = Subscriber(host=self.context.messaging.telemetry.host, 
                              port=self.context.messaging.telemetry.port, 
                              topics=["mavlink_MISSION_ITEM_REACHED"], 
                              callback=self.handler)
        self.sub.start()
        return 0
    
    def compile(self) -> int:
        self.sub = None
        if (len(self.params) != 1 
                or not isinstance(self.params[0], int) 
                or self.params[0] < 0 
                or self.params[0] >= len(self.context.waypoint_missions)):
            self.context.logger.error("Invalid parameters for Waypoint task.")
            return -1
        self.mission_filepath = self.context.waypoint_missions[self.params[0]]

        self.length = get_mission_length(self.mission_filepath)
        if self.length == 0:
            self.context.logger.error("Waypoint mission file is empty or invalid.")
            return -1
        self.mission = Mission(self.context.controller)
        loaded = self.mission.load_mission_from_file(self.mission_filepath)
        if loaded != 0:
            self.context.logger.error("Failed to load waypoint mission from file.")
            return -1
        self.compiled = True
        return 0
    
    async def handler(self, msg: Message) -> None:
        if await is_mission_completed(msg, self.context):
            self.context.logger.info("[Waypoint] Waypoint mission completed.")
            
            await self.sub.close() if self.sub else None
            self.context.task_completed_event.set()

    async def after(self) -> int:
        if self.sub: 
            await self.sub.close()
            self.sub = None
        self.context.task_coroutine = None
        self.context.current_task = None
        self.context.task_completed_event.clear()
        self.context.reset_mission_progress()
        return 0