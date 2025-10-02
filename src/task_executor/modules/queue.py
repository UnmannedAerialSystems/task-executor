# src/task_executor/modules/queue.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-01
# Last Modified: 2025-10-01
# Organization: PSU UAS

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_executor.models.task import Task

class Queue:
    """
    Queue class to manage routine and immediate tasks.
    """
    
    def __init__(self):
        self.routine = asyncio.Queue()
        self.immediate = asyncio.Queue()

    async def add(self, task: "Task") -> int:
        """
        Add a task to the appropriate queue based on its priority.

        Args:
            task (Task): The task to be added.

        Returns:
            int: 0 if the task was added successfully.
        """
        if task.is_immediate():
            print("[Queue] Adding immediate task")
            await self.immediate.put(task)
        else:
            print("[Queue] Adding routine task")
            await self.routine.put(task)
        return 0
    
    async def pop_routine(self) -> int:
        """
        Execute a task from the routine queue if available.

        Returns:
            int: The result of the task execution, or -1 if the queue is empty.
        """
        if self.routine.empty():
            return -1
        task = await self.routine.get()
        print(f"[Queue] Executing routine task: {task.task_id}")
        return await task.execute()
    
    async def pop_immediate(self) -> int:
        """
        Execute a task from the routine queue if available.

        Returns:
            int: The result of the task execution, or -1 if the queue is empty.
        """
        if self.routine.empty():
            return -1
        task = await self.routine.get()
        print(f"[Queue] Executing immediate task: {task.task_id}")
        return await task.execute()