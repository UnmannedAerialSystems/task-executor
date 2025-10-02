# src/task_executor/models/zmq_config.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-01
# Last Modified: 2025-10-01
# Organization: PSU UAS

from task_executor.models.zmq_endpoint import ZMQEndpoint

from pydantic import BaseModel

class ZMQConfig(BaseModel):
    host: str
    telemetry: ZMQEndpoint
    tasks: ZMQEndpoint
