# src/task_executor/tasks/takeoff.py
# version: 1.3.1
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-10-02
# Organization: PSU UAS

from uas_messenger.subscriber import Subscriber
from uas_messenger.message import Message

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

from task_executor.utils.utils import get_mission_length, is_mission_completed

class Takeoff(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)
        self.zmq_sub = None

    async def _do_execute(self) -> int:
        if not self.compiled:
            raise RuntimeError("Task must be compiled before execution.")
        
        if self.mission_filepath is None:
            raise ValueError("Takeoff mission filepath is not available.")
        
        self.context.current_task = self
        self.context.mission_in_progress = True
        self.context.current_mission_length = self.length
        await self.controller.arm()
        await self.controller.takeoff(self.mission_filepath)
        self.sub = Subscriber(host=self.context.messaging.host, 
                              port=self.context.messaging.telemetry.port, 
                              topics=["mavlink_MISSION_ITEM_REACHED"], 
                              callback=self.handler)
        self.sub.start()
        return 0
    
    def compile(self) -> int:
        self.compiled = True
        if self.mission_filepath is None:
            raise ValueError("Takeoff mission filepath is not available.")
        self.length = get_mission_length(self.mission_filepath)
        if self.length == 0:
            raise RuntimeError("Takeoff mission file is empty or invalid.")
        return 0
    
    async def handler(self, msg: Message) -> None:
        if await is_mission_completed(msg, self.context):
            self.context.logger.info("[Takeoff] Takeoff mission completed.")
            await self.sub.close() if self.sub else None
            self.context.task_completed_event.set()

