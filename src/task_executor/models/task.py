# src/task_executor/models/task.py
# version: 1.3.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-10-02
# Organization: PSU UAS

from abc import ABC, abstractmethod

import asyncio
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from task_executor.models.request import Request
    from task_executor.modules.context import Context

IMMEDIATE_PRIORITY = 1
ROUTINE_PRIORITY = 2

class Task(ABC):
    """
    Abstract base class for all tasks.
    """

    def __init__(self, request: "Request", context: "Context"):
        self.request_id = request.request_id
        self.task_id = request.task_id
        self.priority = request.priority
        self.params = request.params
        self.compiled = False
        self.controller = context.controller
        self.mission_filepath = context.task_missions.get(self.task_id, None)
        self.context = context
        self.compile()

    async def execute(self) -> int:
        """
        Execute the task after ensuring it is compiled.

        Returns:
            int: The result of the task execution.
        """
        if not self.compiled:
            raise RuntimeError("Task must be compiled before execution.")
        self.context.task_coroutine = asyncio.create_task(self._do_execute())
        return 0
    
    def is_immediate(self) -> bool:
        """
        Check if the task is of immediate priority.

        Returns:
            bool: True if the task is immediate, False otherwise.
        """
        return self.priority == 1

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

    def after(self) -> int:
        """
        Actions to perform after task execution.

        Returns:
            int: The result of the after execution actions.
        """
        self.context.task_coroutine = None
        self.context.current_task = None
        self.context.task_completed_event.clear()
        self.context.reset_mission_progress()
        return 0