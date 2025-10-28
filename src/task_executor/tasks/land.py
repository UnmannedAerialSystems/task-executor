# src/task_executor/tasks/land.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-30
# Organization: PSU UAS

from uas_messenger.subscriber import Subscriber
from uas_messenger.message import Message

from task_executor.enums.mavlink import MavLandedState, MavMessageType

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

from task_executor.utils.utils import get_mission_length

from MAVez.mission import Mission

class Land(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)
        self.sub = None
        self.last_landed_state = MavLandedState.UNDEFINED


    async def _do_execute(self) -> int:
        if not self.compiled:
            self.context.logger.critical("[Land] Task must be compiled before execution.")
            raise RuntimeError("Task must be compiled before execution.") # throw to crash coroutine
        
        if self.mission_filepath is None:
            self.context.logger.critical("[Land] Takeoff mission filepath is not available.")
            raise ValueError("Takeoff mission filepath is not available.") # throw to crash coroutine
        
        self.context.mission_in_progress = True
        self.context.current_mission_length = self.length
        self.context.current_task = self
        res = await self.controller.set_message_interval(MavMessageType.EXTENDED_SYS_STATE.value, 1000000) # 1 Hz
        if res != 0:
            self.context.logger.error("[Land] Failed to set EXTENDED_SYS_STATE message interval")
            return res
        await self.mission.send_mission()
        await self.controller.set_mode("AUTO")
        self.sub = Subscriber(host=self.context.messaging.host, 
                              port=self.context.messaging.telemetry.port, 
                              topics=["mavlink_EXTENDED_SYS_STATE"], 
                              callback=self.handler)
        self.sub.start()
        return 0
    
    def compile(self) -> int:
        if self.mission_filepath is None:
            self.context.logger.error("[Land] Mission filepath is not available.")
            return -1
        self.length = get_mission_length(self.mission_filepath)
        if self.length == 0:
            self.context.logger.error("[Land] Land mission file is empty or invalid.")
            return -1
        self.mission = Mission(self.context.controller)
        loaded = self.mission.load_mission_from_file(self.mission_filepath)
        if loaded != 0:
            self.context.logger.error("[Land] Failed to load land mission from file.")
            return -1
        self.compiled = True
        return 0
    
    async def handler(self, msg: Message):
        data = msg.header
        landed_state = MavLandedState(data.get("landed_state", MavLandedState.UNDEFINED))

        if landed_state == MavLandedState.UNDEFINED:
            self.context.logger.warning("[Handler] Invalid landed_state received")
    
        elif landed_state == MavLandedState.ON_GROUND:
            self.context.logger.info("[Handler] Land mission completed")
            await self.finish()
            self.context.task_completed_event.set()
        
        # elif landed_state != self.last_landed_state:
        else:
            self.context.logger.info(f"[Handler] Landed state: {landed_state.name}")
            self.last_landed_state = landed_state

    
    async def finish(self) -> int:
        res = await self.controller.disable_message_interval(MavMessageType.EXTENDED_SYS_STATE.value)
        if res != 0:
            self.context.logger.error("[Land] Failed to disable EXTENDED_SYS_STATE message interval")

        await self.sub.close() if self.sub else None

        res = await self.controller.disarm()
        if res != 0:
            self.context.logger.error("[Land] Failed to disarm the vehicle")

        res = await self.controller.set_current_mission_index(0)
        if res != 0:
            self.context.logger.error("[Land] Failed to reset mission index")
        return res
