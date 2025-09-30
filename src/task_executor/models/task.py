# src/task_executor/models/task.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-29
# Organization: PSU UAS

from task_executor.models.request import Request
from task_executor.modules.context import Context

from abc import ABC, abstractmethod

class Task(ABC):

    def __init__(self, request: Request, context: Context):
        self.request_id = request.request_id
        self.task_id = request.task_id
        self.priority = request.priority
        self.params = request.params
        self.compiled = False
        self.controller = context.controller
        self.mission_filepath = context.missions.get(self.task_id, None)
        self.compile()

    async def execute(self) -> int:
        """
        Execute the task after ensuring it is compiled.

        Returns:
            int: The result of the task execution.
        """
        if not self.compiled:
            raise RuntimeError("Task must be compiled before execution.")
        return await self._do_execute()

    @abstractmethod
    async def _do_execute(self) -> int:
        """
        Execute the task.

        Returns:
            int: The result of the task execution.
        """
        pass

    @abstractmethod
    def compile(self) -> int:
        """
        Compile the task.

        Returns:
            int: The result of the task compilation.
        """
        pass