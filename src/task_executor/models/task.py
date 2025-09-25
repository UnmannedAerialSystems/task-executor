# task.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-25
# Organization: PSU UAS

from abc import ABC, abstractmethod
from task_executor.models.request import Request

class Task(ABC):

    def __init__(self, request: Request):
        self.request_id = request.request_id
        self.task_id = request.task_id
        self.priority = request.priority
        self.params = request.params
        self.compile()

    @abstractmethod
    def execute(self) -> int:
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