# airdrop.py
# version: 1.0.0
# Author: 
# Creation Date: 2025-09-25
# Last Modified: 2025-09-25
# Organization: PSU UAS

from task_executor.models.task import Task
from task_executor.models.request import Request

class Airdrop(Task):

    def __init__(self, req: Request, mission_filepath: str):
        super().__init__(req, mission_filepath)

    def _do_execute(self) -> int:
        print("Executing Airdrop Task")
        return 0
    
    def compile(self) -> int:
        print("Compiling Airdrop Task")
        return 0