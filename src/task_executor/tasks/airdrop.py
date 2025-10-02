# src/task_executor/tasks/airdrop.py
# version: 1.1.0
# Author: 
# Creation Date: 2025-09-25
# Last Modified: 2025-10-02
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

class Airdrop(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)

    async def _do_execute(self) -> int:
        self.context.logger.info("Executing Airdrop Task")
        return 0
    
    def compile(self) -> int:
        self.context.logger.info("Compiling Airdrop Task")
        return 0