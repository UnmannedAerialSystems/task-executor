# src/task_executor/tasks/land.py
# version: 1.1.0
# Author: 
# Creation Date: 2025-09-25
# Last Modified: 2025-09-30
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request

from task_executor.modules.context import Context

class Land(Task):

    def __init__(self, req: Request, context: Context):
        super().__init__(req, context)

    async def _do_execute(self) -> int:
        print("Executing Land Task")
        return 0
    
    def compile(self) -> int:
        print("Compiling Land Task")
        return 0