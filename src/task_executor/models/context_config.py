# src/task_executor/models/context_config.py
# version: 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-10-01
# Last Modified: 2025-10-21
# Organization: PSU UAS

from task_executor.models.messenger_config import MessengerConfig
from task_executor.models.logging_config import LoggingConfig

from pydantic import BaseModel

class ContextConfig(BaseModel):
    task_missions: dict[str, str]
    waypoint_missions: list[str]
    messaging: MessengerConfig
    logging: LoggingConfig
