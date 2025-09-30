# src/task_executor/tasks/takeoff.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-30
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

class Takeoff(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)

    async def _do_execute(self) -> int:
        if not self.compiled:
            raise RuntimeError("Task must be compiled before execution.")
        
        if self.mission_filepath is None:
            raise ValueError("Takeoff mission filepath is not available.")
            
        await self.controller.arm()
        await self.controller.takeoff(self.mission_filepath)
        return 0
    
    def compile(self) -> int:
        self.compiled = True
        return 0