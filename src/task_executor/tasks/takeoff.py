# takeoff.py
# version: 1.0.0
# Author: 
# Creation Date: 2025-09-25
# Last Modified: 2025-09-25
# Organization: PSU UAS

from task_executor.models.task import Task

class Takeoff(Task):
    def _do_execute(self) -> int:
        print("Executing Takeoff Task")
        return 0
    
    def compile(self) -> int:
        print("Compiling Takeoff Task")
        return 0