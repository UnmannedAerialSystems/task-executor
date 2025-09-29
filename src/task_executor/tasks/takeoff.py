# takeoff.py
# version: 1.1.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-29
# Organization: PSU UAS

from task_executor.models.config import Config
from task_executor.models.task import Task
from task_executor.models.request import Request
from MAVez.mission import Mission

class Takeoff(Task):

    def __init__(self, req: Request, config: Config):
        super().__init__(req, config)

    async def _do_execute(self) -> int:
        if not self.compiled:
            raise RuntimeError("Task must be compiled before execution.")
        # await self.mission.send_mission()
        await self.controller.arm()
        await self.controller.takeoff(self.mission_filepath)
        return 0
    
    def compile(self) -> int:
        # if self.mission_filepath is None:
        #     raise ValueError("Takeoff mission filepath is not provided in the configuration.")
        # self.mission = Mission(self.controller)
        # self.mission.load_mission_from_file(self.mission_filepath)
        # print(self.mission)
        self.compiled = True
        return 0