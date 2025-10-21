# src/task_executor/models/messenger_config.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-21
# Last Modified: 2025-10-21
# Organization: PSU UAS

from task_executor.models.message_endpoint import MessageEndpoint

from pydantic import BaseModel

class MessengerConfig(BaseModel):
    host: str
    telemetry: MessageEndpoint
    tasks: MessageEndpoint
