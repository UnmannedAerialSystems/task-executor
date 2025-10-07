# src/task_executor/models/context_config.py
# version: 1.1.0
# Author: Theodore Tasman
# Creation Date: 2025-10-01
# Last Modified: 2025-10-02
# Organization: PSU UAS

from task_executor.models.zmq_config import ZMQConfig
from task_executor.models.logging_config import LoggingConfig

from pydantic import BaseModel

class ContextConfig(BaseModel):
    task_missions: dict[str, str]
    waypoint_missions: list[str]
    zmq: ZMQConfig
    logging: LoggingConfig
