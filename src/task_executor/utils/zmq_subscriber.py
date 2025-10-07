# src/task_executor/utils/config.py
# version 1.1.0
# Author: Theodore Tasman
# Creation Date: 2025-09-29
# Last Modified: 2025-09-29

import asyncio
import zmq
from collections.abc import Callable
from MAVez.safe_logger import SafeLogger

class ZMQSubscriber:
    def __init__(self, host: str, port: int, topic: str, logger: SafeLogger):
        self.ctx = zmq.Context()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(f"tcp://{host}:{port}")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.sub.setsockopt(zmq.LINGER, 0)
        self.sub.setsockopt(zmq.RCVHWM, 1)
        self.topic = topic
        self.running = False
        self.port = port
        self.logger = logger

    def recv(self, flags: int = 0, timeout: int = 1000) -> tuple[str, str] | tuple[None, None]:
        try:
            poller = zmq.Poller()
            poller.register(self.sub, zmq.POLLIN)
            socks = dict(poller.poll(timeout))
            if self.sub in socks and socks[self.sub] == zmq.POLLIN:
                raw = self.sub.recv_string(flags=flags)
                if raw is None:
                    return None, None
                topic, payload = raw.split(" ", 1)
                return topic, payload
            return None, None
        except zmq.Again:
            return None, None
        except Exception as e:
            self.logger.error(f"[ZMQSubscriber] Error: {e}")
            return None, None
        
    async def start(self, handler: Callable):
        """
        Start the subscriber.
        """
        # self.drain_old()
        self.running = True
        loop = asyncio.get_running_loop()
        try:
            while self.running:
                topic, msg = await loop.run_in_executor(None, self.recv)

                if msg is None or topic is None:
                    continue
                
                if self.topic in topic:
                    result = await handler(msg)
                    if result == 0:
                        self.logger.info(f"[ZMQSubscriber] Handler signaled to stop for topic {self.topic}")
                        break

                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            self.logger.info(f"[ZMQSubscriber] Subscription to {self.topic} stopped")
            raise
        except Exception as e:
            self.logger.error(f"[ZMQSubscriber] Error: {e}")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        try:
            self.sub.close(0)
        except Exception:
            self.logger.error(f"[ZMQSubscriber] Failed to close socket on port {self.port}")
        try:
            self.ctx.term()
        except Exception:
            self.logger.error(f"[ZMQSubscriber] Failed to terminate context on port {self.port}")
