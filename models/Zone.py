from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class ZoneTypes(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ValidateZone(BaseModel):
    name: str = Field(
        description="Name of the zone"
    ),
    x: int = Field(
        ge=0, description="X of zone's coordinate"
    ),
    y: int = Field(
        ge=0, description="Y of zone's coordinate"
    ),
    zone_type: ZoneTypes = Field(
        ZoneTypes.NORMAL.value,
        description="Type of the zone, default normal"
    ),
    max_drones: int = Field(
        1, ge=0,
        description="Maximum drones that can occupy this zone simultaneously"
    ),
    color: str = Field(
        None, description="Color of the zone"
    ),
    current_drones: int = Field(
        0, ge=0, description="To track the number of the current drones"
    )


class Zone:
    def __init__(
        self, name: str, x: int, y: int, zone_type: ZoneTypes,
        max_drones: int, color: Optional[str] = None,
        current_drones: Optional[int] = 0
    ) -> None:
        valid_zone = ValidateZone(
            name, x, y, zone_type, max_drones, color,
            current_drones
        )
        self.name: str = valid_zone.name
        self.x: int = valid_zone.x
        self.y: int = valid_zone.y
        self.zone_type: ZoneTypes = valid_zone.zone_type
        self.max_drones: int = valid_zone.max_drones
        self.color: str = valid_zone.color
        self.current_drones: int = valid_zone.current_drones
