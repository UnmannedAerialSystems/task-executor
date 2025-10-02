# src/task_executor/models/zmq_endpoint.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-01
# Last Modified: 2025-10-01
# Organization: PSU UAS

from pydantic import BaseModel

class ZMQEndpoint(BaseModel):
    port: int
    topic: str