# src/task_executor/enums/mavlink.py
# version: 1.0.0
# Author: Theodore Tasman
# Creation Date: 2025-10-02
# Last Modified: 2025-10-02
# Organization: PSU UAS

from enum import Enum

class MavLandedState(Enum):
    """
    Enum for MAVLink landed states.
    """
    UNDEFINED = 0
    ON_GROUND = 1
    IN_AIR = 2
    TAKING_OFF = 3
    LANDING = 4

class MavMessageType(Enum):
    """
    Enum for MAVLink message types.
    """
    EXTENDED_SYS_STATE = 245