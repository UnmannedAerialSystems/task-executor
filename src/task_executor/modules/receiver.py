# src/task_executor/modules/receiver.py
# version 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-06
# Last Modified: 2025-10-06

import json
from task_executor.models.request import Request

from task_executor.modules.context import Context
from task_executor.modules.catalog import Catalog

from task_executor.utils.zmq_subscriber import ZMQSubscriber

import asyncio

class Receiver:
    """
    Receiver class to listen for task requests via ZeroMQ.
    """
    
    def __init__(self, context: Context):
        self.running = True
        self.context = context
        self.zmq_sub = ZMQSubscriber(
            host=context.zmq.host,
            port=context.zmq.tasks.port,
            topic=context.zmq.tasks.topic,
            logger=context.logger
        )
        self.catalog = Catalog(context)

    async def start(self):
        """
        Start the receiver to listen for messages.
        """
        try:
            await self.zmq_sub.start(self.handle_request)
            while self.running:
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            self.context.logger.info("[Monitor] Monitor stopped")
            raise

        except Exception as e:
            self.context.logger.error(f"[Monitor] Error: {e}")
            
        finally:
            self.zmq_sub.stop()
            self.stop()

    async def handle_request(self, msg: str):
        """
        Handle incoming task request messages.
        """
        request = Request.from_json(json.loads(msg))
        if request is None:
            self.context.logger.error("[Receiver] Invalid request format.")
            print(request)
            return -1  # Continue listening
        else:
            task = self.catalog.get_task(request)
            if task:
                await self.context.queue.add(task)
            else:
                self.context.logger.error(f"[Receiver] Unknown task ID: {request.task_id}")
        return -1  # Continue listening

    def stop(self):
        """
        Stop the monitor.
        """
        self.running = False


