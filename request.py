import json

class Request:

    def __init__(self, request_id: int, task_id: str, priority: int, params: list):
        self.request_id = request_id
        self.task_id = task_id
        self.priority = priority
        self.params = params

    @classmethod
    def from_json(cls, json_data: str):
        """
        Create a Request instance from JSON data.

        Args:
            json_data (str): JSON string representing the request.

        Returns:
            Request: An instance of the Request class.
        """
        data = json.loads(json_data)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Request instance from a dictionary.

        Args:
            data (dict): Dictionary representing the request.

        Returns:
            Request: An instance of the Request class.
        """
        request_id = data.get('request_id')
        if request_id is None:
            raise ValueError("request_id is required and cannot be None")
        task_id = data.get('task_id')
        if task_id is None:
            raise ValueError("task_id is required and cannot be None")
        priority = data.get('priority', 0)
        params = data.get('params', [])
        return cls(
            request_id=request_id,
            task_id=task_id,
            priority=priority,
            params=params
        )
    
    def to_dict(self) -> dict:
        """
        Convert the Request instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Request instance.
        """
        return {
            'request_id': self.request_id,
            'task_id': self.task_id,
            'priority': self.priority,
            'params': self.params
        }

    def to_json(self) -> str:
        """
        Convert the Request instance to a JSON string.

        Returns:
            str: A JSON string representation of the Request instance.
        """
        return json.dumps(self.to_dict())

    def __repr__(self):
        return f"Request(request_id={self.request_id}, task_id='{self.task_id}', priority={self.priority}, params={self.params})"
    
    __str__ = __repr__