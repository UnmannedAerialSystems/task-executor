# src/task_executor/modules/config.py
# version 1.0.1
# Author: Theodore Tasman
# Creation Date: 2025-09-29
# Last Modified: 2025-09-29

from task_executor.modules.context import Context
from task_executor.utils.zmq_subscriber import ZMQSubscriber

import json
import time
import asyncio

class Monitor:
    def __init__(self, context: Context):
        self.subscriber = ZMQSubscriber(host=context.zmq_host, port=context.zmq_port, topic=context.zmq_topic)
        self.running = True

    async def start(self):
        loop = asyncio.get_running_loop()
        try:
            while self.running:
                topic, msg = await loop.run_in_executor(None, self.subscriber.recv)

                if msg is None or topic is None:
                    continue
                
                if "MISSION_ITEM_REACHED" in topic:
                    data = json.loads(msg)
                    print(f"[Monitor] MISSION_ITEM_REACHED: {data.get('seq', 'N/A')}")

                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            print("[Monitor] Monitor stopped")
            raise
        finally:
            self.stop()

    def stop(self):
        """Stop the monitor."""
        self.running = False
