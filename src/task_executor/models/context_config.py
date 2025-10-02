# src/task_executor/models/context_config.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-01
# Last Modified: 2025-10-01
# Organization: PSU UAS

from task_executor.models.zmq_config import ZMQConfig

from pydantic import BaseModel

class ContextConfig(BaseModel):
    missions: dict[str, str]
    zmq: ZMQConfig
