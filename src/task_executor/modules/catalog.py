# catalog.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-09-25
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request
from task_executor.models.config import Config

# begin task imports
from task_executor.tasks.airdrop import Airdrop
from task_executor.tasks.detect import Detect
from task_executor.tasks.land import Land
from task_executor.tasks.takeoff import Takeoff
from task_executor.tasks.waypoint import Waypoint
# end task imports

class Catalog:
    """
    A catalog that maps task IDs to their corresponding Task classes.
    """
    __TASK_CATALOG = {
        "airdrop": Airdrop,
        "detect": Detect,
        "land": Land,
        "takeoff": Takeoff,
        "waypoint": Waypoint,
    }

    def __init__(self, config: Config):
        self.config = config

    def get_task(self, request: Request) -> Task:
        """
        Retrieve a Task instance based on the given task ID.

        Args:
            task_id (str): The ID of the task.

        Returns:
            Task: An instance of a class that implements the Task interface.
        """
        task_class = self.__TASK_CATALOG.get(request.task_id)
        if task_class is None:
            raise ValueError(f"No task found for task ID: {request.task_id}")
        return task_class(request, self.config)
