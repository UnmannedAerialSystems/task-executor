# src/task_executor/tasks/waypoint.py
# version: 1.1.0
# Author: Theodore Tasman
# Creation Date: 2025-09-29
# Last Modified: 2025-10-02
# Organization: PSU UAS

import json


def get_mission_length(filepath: str) -> int:
    """
    Utility function to get the number of mission items in a mission file.

    Args:
        filepath (str): Path to the mission file.

    Returns:
        int: Number of mission items in the file.
    """
    try:
        with open(filepath, 'r') as f:
            return len(f.readlines()) - 1  # Subtract 1 for the header line
    except Exception as e:
        return 0
    

async def is_mission_completed(msg, context) -> int:
    """
    Wait for the mission to complete by monitoring the current mission index.

    Args:
        length (int): Total number of mission items.
        context (Context): The application context.
    """
    data = json.loads(msg)
    seq = data.get("seq", -1)
    if seq == -1:
        context.logger.warning("[Handler] Invalid seq number received")
    elif seq == context.current_mission_length - 1:
        context.logger.info("[Handler] Mission completed")
        return True
    context.logger.info(f"[Handler] Current mission seq: {seq}")
    return False