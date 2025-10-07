# zmq_broker.py
# version: 1.1.1
# Original Author: Theodore Tasman
# Creation Date: 2025-09-24
# Last Modified: 2025-09-24
# Organization: PSU UAS

from typing import Any
import zmq
import json

class ZMQBroker():
    """
    A ZeroMQ broker for publishing messages. 

    Args:
        host (str): The hostname to bind the ZeroMQ socket. Default is "localhost".
        port (int): The port number to bind the ZeroMQ socket. Default is 5555.
    """

    def __init__(self, host: str = "localhost", port: int = 5555):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://{self.host}:{self.port}")
        self.socket.setsockopt(zmq.LINGER, 0)

    async def publish(self, topic: str, message: Any) -> None:
        """
        Publish a message to a specified topic. The topic will be combined with the message type.

        Args:
            topic (str): The topic to publish the message to.

        Returns:
            None
        """
        self.socket.send_string(f"{topic} {json.dumps(message)}")

    def close(self) -> None:
        """
        Close the ZeroMQ socket and terminate the context.

        Returns:
            None
        """
        self.socket.close()
        self.context.term()
