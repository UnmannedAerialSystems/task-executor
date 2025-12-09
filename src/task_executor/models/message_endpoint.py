# src/task_executor/models/message_endpoint.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-21
# Last Modified: 2025-10-21
# Organization: PSU UAS

from pydantic import BaseModel

class MessageEndpoint(BaseModel):
    host: str
    port: int
    topic: str