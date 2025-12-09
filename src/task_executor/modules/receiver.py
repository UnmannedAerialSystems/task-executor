# src/task_executor/modules/receiver.py
# version 1.0.1
# Author: Theodore Tasman
# Creation Date: 2025-10-06
# Last Modified: 2025-12-09

from uas_messenger.subscriber import Subscriber
from uas_messenger.message import Message

from task_executor.models.request import Request

from task_executor.modules.context import Context
from task_executor.modules.catalog import Catalog


import asyncio

class Receiver:
    """
    Receiver class to listen for task requests via ZeroMQ.
    """
    
    def __init__(self, context: Context):
        self.running = True
        self.context = context
        self.sub = Subscriber(
            host=context.messaging.tasks.host,
            port=context.messaging.tasks.port,
            topics=[context.messaging.tasks.topic],
            callback=self.handle_request
        )
        self.catalog = Catalog(context)

    async def start(self):
        """
        Start the receiver to listen for messages.
        """
        try:
            self.sub.start()
            while self.running:
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            self.context.logger.info("[Receiver] Receiver stopped")

        except Exception as e:
            self.context.logger.error(f"[Receiver] Error: {e}")

        finally:
            await self.sub.close()
            self.stop()

    async def handle_request(self, msg: Message):
        """
        Handle incoming task request messages.
        """
        request = Request.from_dict(msg.header)
        if request is None:
            self.context.logger.error("[Receiver] Invalid request format.")
            print(request)
        else:
            task = self.catalog.get_task(request)
            if task:
                await self.context.queue.add(task)
            else:
                self.context.logger.error(f"[Receiver] Failed to retrieve task: {request.task_id}")

    def stop(self):
        """
        Stop the monitor.
        """
        self.running = False


