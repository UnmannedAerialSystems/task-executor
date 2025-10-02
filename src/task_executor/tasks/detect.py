# src/task_executor/tasks/detect.py
# version: 1.1.1
# Author: 
# Creation Date: 2025-09-25
# Last Modified: 2025-09-30
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

class Detect(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)

    async def _do_execute(self) -> int:
        self.context.logger.info("Executing Detect Task")
        return 0
    
    def compile(self) -> int:
        self.context.logger.info("Compiling Detect Task")
        return 0