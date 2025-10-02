# src/task_executor/models/request.py
# version: 1.1.0
# Author: Theodore Tasman
# Creation Date: 2025-09-25
# Last Modified: 2025-10-01
# Organization: PSU UAS

from typing import Any, List
from pydantic import BaseModel, Field

class Request(BaseModel):
    """
    A class representing a task request.
    """

    request_id: int
    task_id: str
    priority: int = Field(default=0)
    params: List[Any] = Field(default_factory=list)

    @classmethod
    def from_json(cls, json_data: str) -> "Request":
        """Create a Request instance from a JSON string."""
        return cls.model_validate_json(json_data)

    @classmethod
    def from_dict(cls, data: dict) -> "Request":
        """Create a Request instance from a dictionary."""
        return cls.model_validate(data)

    def to_dict(self) -> dict:
        """Convert the Request instance to a dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert the Request instance to a JSON string."""
        return self.model_dump_json()
