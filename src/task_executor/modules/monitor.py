# src/task_executor/modules/config.py
# version 1.2.0
# Author: Theodore Tasman
# Creation Date: 2025-09-29
# Last Modified: 2025-10-02

from task_executor.modules.context import Context
from task_executor.utils.zmq_subscriber import ZMQSubscriber

import asyncio

class Monitor:
    """
    Monitor class to listen for specific messages via ZeroMQ.
    """
    
    def __init__(self, context: Context):
        self.subscriber = ZMQSubscriber(host=context.zmq.host, port=context.zmq.tasks.port, topic=context.zmq.tasks.topic)
        self.running = True
        self.context = context

    async def start(self):
        """
        Start the monitor to listen for messages.
        """
        try:
            while self.running:

                if self.context.task_completed_event.is_set():
                    self.context.task_completed_event.clear()
                    self.context.reset_mission_progress()
                    print("[Monitor] Task completed")

                    res = await self.context.queue.pop_routine()
                    if res == -1:
                        print("[Monitor] No routine tasks to execute.")
                    else:
                        print(f"[Monitor] Executed routine task with result: {res}")

                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            print("[Monitor] Monitor stopped")
            raise

        except Exception as e:
            print(f"[Monitor] Error: {e}")
            
        finally:
            self.stop()

    def stop(self):
        """
        Stop the monitor.
        """
        self.running = False


