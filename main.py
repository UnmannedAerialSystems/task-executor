from task_executor.models.context_config import ContextConfig
from task_executor.models.request import Request
from task_executor.models.task import IMMEDIATE_PRIORITY, ROUTINE_PRIORITY

from task_executor.modules.catalog import Catalog
from task_executor.modules.context import Context
from task_executor.modules.monitor import Monitor

import asyncio
import signal
import sys

from task_executor.modules.receiver import Receiver
from testing.delayed_trigger import delayed_trigger

WAYPOINT_FILE_PATH = "missions/waypoint.txt"
DETECT_FILE_PATH = "missions/detect.txt"
TAKEOFF_FILE_PATH = "missions/takeoff.txt"
LANDING_FILE_PATH = "missions/landing.txt"

# Global flag for shutdown
shutdown_event = asyncio.Event()

def signal_handler():
    """Handle shutdown signals gracefully."""
    print("\nReceived shutdown signal...")
    shutdown_event.set()

async def main():

    # initialize context
    config = {
        "task_missions": {
            "takeoff": TAKEOFF_FILE_PATH,
            "land": LANDING_FILE_PATH,
        },
        "waypoint_missions": [
            WAYPOINT_FILE_PATH,
            DETECT_FILE_PATH
        ],
        "messaging": {   
            "host": "127.0.0.1", 
            "telemetry": {
                "port": 5555,
                "topic": "mavlink",
            },
            "tasks": {
                "port": 5556,
                "topic": "task_request"
            }
        },
        "logging": {
            "level": "INFO",
            "directory": "flight_logs",
        }
    }
    try:
        context = Context(ContextConfig.model_validate(config))
    except Exception as e:
        print(f"Configuration Error: {e}")
        return
    
    # start flight controller messaging
    await context.controller.start()

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    if sys.platform != 'win32':
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    else:
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())

    # Initialize monitor
    monitor = Monitor(context)
    monitor_task = asyncio.create_task(monitor.start())

    # Initialize receiver
    receiver = Receiver(context)
    receiver_task = asyncio.create_task(receiver.start())


    catalog = Catalog(context)

    takeoff_task = catalog.get_task(
        Request(
            request_id=1,
            task_id="takeoff",
            priority=ROUTINE_PRIORITY,
            params=[]
        )
    )

    detect_task = catalog.get_task(
        Request(
            request_id=2,
            task_id="waypoint",
            priority=ROUTINE_PRIORITY,
            params=[1]
        )
    )

    waypoint_task = catalog.get_task(
        Request(
            request_id=3,
            task_id="waypoint",
            priority=ROUTINE_PRIORITY,
            params=[0]
        )
    )

    landing_task = catalog.get_task(
        Request(
            request_id=4,
            task_id="land",
            priority=ROUTINE_PRIORITY,
            params=[]
        )
    )

    immediate_landing_task = catalog.get_task(
        Request(
            request_id=5,
            task_id="land",
            priority=IMMEDIATE_PRIORITY,
            params=[]
        )
    )

    try:
        # print("\nExecuting Tasks...")
        # await takeoff_task.execute()
        # await context.queue.add(detect_task)
        # await context.queue.add(waypoint_task)
        # await context.queue.add(landing_task)

        # print("Task completed. Monitoring... (Ctrl+C to exit)")

        # await delayed_trigger(30)
        # await context.queue.add(immediate_landing_task)
        
        # Wait for shutdown signal instead of infinite loop
        await shutdown_event.wait()

        
    except KeyboardInterrupt:
        print("\nReceived Ctrl+C...")
    finally:
        print("Shutting down...")
        
        # Cancel monitor task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        # Cancel receiver task
        receiver_task.cancel()
        try:
            await receiver_task
        except asyncio.CancelledError:
            pass
        
        # Cancel running task if any
        if context.task_coroutine and context.task_coroutine.cancel():
            try:
                await context.task_coroutine
            except asyncio.CancelledError:
                pass

        # Stop controller
        await context.controller.stop()
        
        # Shutdown the executor threads properly
        try:
            loop = asyncio.get_running_loop()
            await loop.shutdown_default_executor()
        except Exception as e:
            print(f"Warning: Could not shutdown executor: {e}")
        
        # Wait a bit for cleanup
        await asyncio.sleep(0.1)
        
        print("Shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        # Force exit if needed
        import os
        os._exit(0)