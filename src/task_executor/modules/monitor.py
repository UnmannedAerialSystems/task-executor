# src/task_executor/modules/monitor.py
# version 1.3.0
# Author: Theodore Tasman
# Creation Date: 2025-09-29
# Last Modified: 2025-10-02

from task_executor.modules.context import Context

import asyncio

class Monitor:
    """
    Monitor class to listen for specific messages via ZeroMQ.
    """
    
    def __init__(self, context: Context):
        self.running = True
        self.context = context
        self.waiting_for_task = False

    async def start(self):
        """
        Start the monitor to listen for messages.
        """
        try:
            while self.running:
                
                if not self.context.queue.immediate.empty():
                    self.context.logger.info("[Monitor] Immediate task detected.")
                    self.context.task_coroutine.cancel() if self.context.task_coroutine else None
                    self.context.current_task.after() if self.context.current_task else None
                    res = await self.context.queue.pop_immediate()
                    if res == 1:
                        if not self.waiting_for_task:
                            self.context.logger.warning("[Monitor] No immediate tasks to execute.")
                            self.waiting_for_task = True
                    elif res == -1:
                        self.context.logger.warning("[Monitor] Failed to execute immediate task.")
                    else:
                        self.context.logger.info(f"[Monitor] Executed immediate task with result: {res}")
                        self.waiting_for_task = False

                if self.context.task_completed_event.is_set():
                    if self.context.current_task:
                        self.context.current_task.after()

                    if not self.waiting_for_task:   
                        self.context.logger.info("[Monitor] Task completed")

                    res = await self.context.queue.pop_routine()
                    if res == 1:
                        if not self.waiting_for_task:
                            self.context.logger.warning("[Monitor] No routine tasks to execute.")
                            self.waiting_for_task = True
                    elif res == -1:
                        self.context.logger.warning("[Monitor] Failed to execute routine task.")
                    else:
                        self.context.logger.info(f"[Monitor] Executed routine task with result: {res}")
                        self.waiting_for_task = False
                        self.context.task_completed_event.clear()

                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            self.context.logger.info("[Monitor] Monitor stopped")

        except Exception as e:
            self.context.logger.error(f"[Monitor] Error: {e}")
            
        finally:
            self.stop()

    def stop(self):
        """
        Stop the monitor.
        """
        self.running = False


