# src/task_executor/tasks/waypoint.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-10-02
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

from task_executor.utils.utils import get_mission_length, is_mission_completed
from task_executor.utils.zmq_subscriber import ZMQSubscriber

from MAVez.mission import Mission

class Waypoint(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)

    async def _do_execute(self) -> int:
        if not self.compiled:
            self.context.logger.error("Waypoint task not compiled.")
            raise RuntimeError("Task must be compiled before execution.")
        
        if self.mission_filepath is None:
            self.context.logger.error("Waypoint mission filepath is not available.")
            raise ValueError("Takeoff mission filepath is not available.")
        
        self.context.mission_in_progress = True
        self.context.current_mission_length = self.length
        self.context.current_task = self

        await self.mission.send_mission()
        await self.controller.set_mode("AUTO")
        self.zmq_sub = ZMQSubscriber(self.context.zmq.host, self.context.zmq.telemetry.port, "mavlink_MISSION_ITEM_REACHED", self.context.logger)
        await self.zmq_sub.start(self.handler)
        return 0
    
    def compile(self) -> int:
        self.zmq_sub = None
        if (len(self.params) != 1 
                or not isinstance(self.params[0], int) 
                or self.params[0] < 0 
                or self.params[0] >= len(self.context.waypoint_missions)):
            raise ValueError("Waypoint task requires a single integer parameter representing the waypoint mission index.")
        self.mission_filepath = self.context.waypoint_missions[self.params[0]]

        self.length = get_mission_length(self.mission_filepath)
        if self.length == 0:
            raise RuntimeError("Waypoint mission file is empty or invalid.")
        self.mission = Mission(self.context.controller)
        loaded = self.mission.load_mission_from_file(self.mission_filepath)
        if loaded != 0:
            raise RuntimeError("Failed to load waypoint mission from file.")
        self.compiled = True
        return 0
    
    async def handler(self, msg: str) -> int:
        if await is_mission_completed(msg, self.context):
            self.context.logger.info("[Waypoint] Waypoint mission completed.")
            
            self.zmq_sub.stop() if self.zmq_sub else None
            self.context.task_completed_event.set()
            return 0
        return -1
