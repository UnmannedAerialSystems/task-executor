# src/task_executor/tasks/land.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-30
# Organization: PSU UAS

import json

from task_executor.enums.mavlink import MavLandedState, MavMessageType

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

from task_executor.utils.utils import get_mission_length
from task_executor.utils.zmq_subscriber import ZMQSubscriber

from MAVez.mission import Mission

class Land(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)
        self.zmq_sub = None
        self.last_landed_state = MavLandedState.UNDEFINED


    async def _do_execute(self) -> int:
        if not self.compiled:
            raise RuntimeError("Task must be compiled before execution.")
        
        if self.mission_filepath is None:
            raise ValueError("Takeoff mission filepath is not available.")
        
        self.context.mission_in_progress = True
        self.context.current_mission_length = self.length
        self.context.current_task = self
        res = await self.controller.set_message_interval(MavMessageType.EXTENDED_SYS_STATE.value, 1000000) # 1 Hz
        if res != 0:
            self.context.logger.error("[Land] Failed to set EXTENDED_SYS_STATE message interval")
            return res
        await self.mission.send_mission()
        await self.controller.set_mode("AUTO")
        self.zmq_sub = ZMQSubscriber(self.context.zmq.host, self.context.zmq.telemetry.port, "mavlink_EXTENDED_SYS_STATE", self.context.logger)
        await self.zmq_sub.start(self.handler)
        return 0
    
    def compile(self) -> int:
        if self.mission_filepath is None:
            raise ValueError("Land mission filepath is not available.")
        self.length = get_mission_length(self.mission_filepath)
        if self.length == 0:
            raise RuntimeError("Land mission file is empty or invalid.")
        self.mission = Mission(self.context.controller)
        loaded = self.mission.load_mission_from_file(self.mission_filepath)
        if loaded != 0:
            raise RuntimeError("Failed to load land mission from file.")
        self.compiled = True
        return 0
    
    async def handler(self, msg: str) -> int:
        data = json.loads(msg)
        landed_state = MavLandedState(data.get("landed_state", MavLandedState.UNDEFINED))

        if landed_state == MavLandedState.UNDEFINED:
            self.context.logger.warning("[Handler] Invalid landed_state received")
    
        elif landed_state == MavLandedState.ON_GROUND:
            self.context.logger.info("[Handler] Land mission completed")
            await self.finish()
            self.context.task_completed_event.set()
            return 0
        
        elif landed_state != self.last_landed_state:
            self.context.logger.info(f"[Handler] Landed state: {landed_state.name}")
            self.last_landed_state = landed_state

        return -1
    
    async def finish(self) -> int:
        res = await self.controller.disable_message_interval(MavMessageType.EXTENDED_SYS_STATE.value)
        if res != 0:
            self.context.logger.error("[Land] Failed to disable EXTENDED_SYS_STATE message interval")

        self.zmq_sub.stop() if self.zmq_sub else None

        res = await self.controller.disarm()
        if res != 0:
            self.context.logger.error("[Land] Failed to disarm the vehicle")

        res = await self.controller.set_current_mission_index(0)
        if res != 0:
            self.context.logger.error("[Land] Failed to reset mission index")
        return res
