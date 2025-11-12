from task_executor.models.context_config import ContextConfig
from task_executor.models.request import Request
from task_executor.models.task import IMMEDIATE_PRIORITY, ROUTINE_PRIORITY

from task_executor.modules.catalog import Catalog
from task_executor.modules.context import Context
from task_executor.modules.monitor import Monitor

import asyncio
import signal
import sys
import argparse

from task_executor.modules.receiver import Receiver
from testing.delayed_trigger import delayed_trigger

WAYPOINT_PATH_0 = "missions/test-flight/wp_0.txt"
WAYPOINT_PATH_1 = "missions/test-flight/wp_1.txt"
AIRDROP_PATH = "missions/test-flight/airdrop.txt"
TAKEOFF_DIRECTORY = "missions/test-flight/takeoff"
LAND_DIRECTORY = "missions/test-flight/land"

# Global flag for shutdown
shutdown_event = asyncio.Event()

def signal_handler():
    """Handle shutdown signals gracefully."""
    print("\nReceived shutdown signal...")
    shutdown_event.set()

async def main():
    # Parse direction argument
    parser = argparse.ArgumentParser()
    parser.add_argument("direction", type=str, help="Takeoff/landing direction (ne, nw, se, sw)")
    args = parser.parse_args()
    dir = args.direction.lower()

    if dir not in ["ne", "nw", "se", "sw"]:
        print("[error] Direction argument must be ne, nw, se, or sw")
        return
    
    # initialize context
    config = {
        "task_missions": {
            "takeoff": f"{TAKEOFF_DIRECTORY}/{dir}.txt",
            "land": f"{LAND_DIRECTORY}/{dir}.txt",
        },
        "waypoint_missions": [
            WAYPOINT_PATH_0,
            WAYPOINT_PATH_1
        ],
        "airdrop_missions": [
            AIRDROP_PATH
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
    if not takeoff_task:
        print("[error] Takeoff task could not be created.")
        return

    waypoint_0_task = catalog.get_task(
        Request(
            request_id=2,
            task_id="waypoint",
            priority=ROUTINE_PRIORITY,
            params=[0]
        )
    )
    if not waypoint_0_task:
        print("[error] Waypoint 0 task could not be created.")
        return

    waypoint_1_task = catalog.get_task(
        Request(
            request_id=3,
            task_id="waypoint",
            priority=ROUTINE_PRIORITY,
            params=[1]
        )
    )
    if not waypoint_1_task:
        print("[error] Waypoint 1 task could not be created.")
        return

    landing_task = catalog.get_task(
        Request(
            request_id=4,
            task_id="land",
            priority=ROUTINE_PRIORITY,
            params=[]
        )
    )
    if not landing_task:
        print("[error] Landing task could not be created.")
        return

    immediate_landing_task = catalog.get_task(
        Request(
            request_id=5,
            task_id="land",
            priority=IMMEDIATE_PRIORITY,
            params=[]
        )
    )
    if not immediate_landing_task:
        print("[error] Immediate landing task could not be created.")
        return

    try:
        print("\nExecuting Tasks...")
        await takeoff_task.execute()
        await context.queue.add(landing_task)

        print("Task completed. Monitoring... (Ctrl+C to exit)")

        await delayed_trigger(30)
        await context.queue.add(immediate_landing_task)
        
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