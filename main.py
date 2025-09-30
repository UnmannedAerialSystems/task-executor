from task_executor.models.request import Request

from task_executor.modules.catalog import Catalog
from task_executor.modules.context import Context
from task_executor.modules.monitor import Monitor

import asyncio
import signal
import sys


WAYPOINT_FILE_PATH = "missions/waypoint.txt"
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
        "missions": {
            "waypoint": WAYPOINT_FILE_PATH,
            "takeoff": TAKEOFF_FILE_PATH,
            "land": LANDING_FILE_PATH
        },
        "zmq": {
            "host": "127.0.0.1", 
            "port": 5555
        }
    }
    context = Context(config)
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



    catalog = Catalog(context)

    takeoff_task = catalog.get_task(
        Request(
            request_id=1,
            task_id="takeoff",
            priority=1,
            params=[]
        )
    )

    try:
        print("\nExecuting Tasks...")
        await takeoff_task.execute()

        print("Task completed. Monitoring... (Ctrl+C to exit)")
        
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