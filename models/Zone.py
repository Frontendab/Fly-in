from pydantic import (
    BaseModel, Field, field_validator
)
from pydantic_core import PydanticCustomError
from enum import Enum
from typing import Optional, Union
from pygame.colordict import THECOLORS


class ZoneTypes(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ValidateZone(BaseModel):
    name: str = Field(
        min_length=4, description="Name of the zone"
    )
    x: int = Field(
        ge=0, description="X of zone's coordinate"
    )
    y: int = Field(
        ge=0, description="Y of zone's coordinate"
    )
    zone_type: ZoneTypes = Field(
        ZoneTypes.NORMAL,
        description="Type of the zone, default normal"
    )
    color: Union[str, tuple, None] = Field(
        None, min_length=3, description="Color of the zone"
    )
    max_drones: int = Field(
        1, ge=1,
        description="Maximum drones that can occupy this zone simultaneously"
    )
    current_drones: int = Field(
        0, ge=0, description="To track the number of the current drones"
    )

    @field_validator('color', mode="after")
    def initialize_color(color: str) -> object:
        if isinstance(color, tuple):
            return color

        color_tuple: tuple | None = color
        if color:
            color_tuple = THECOLORS.get(color.lower())
            if not color_tuple:
                raise PydanticCustomError(
                    "invalid_color",
                    (
                        "Invalid color name. " +
                        "See: https://www.pygame.org/docs/ref/color_list.html"
                    )
                )
        return color_tuple


class Zone:
    def __init__(
        self, name: str, x: int, y: int,
        zone_type: Optional[ZoneTypes] = ZoneTypes.NORMAL,
        max_drones: Optional[int] = 1, color: Optional[str] = None,
        current_drones: Optional[int] = 0
    ) -> None:
        valid_zone = ValidateZone(
            name=name, x=x, y=y, zone_type=zone_type, max_drones=max_drones,
            color=color, current_drones=current_drones
        )
        self.name: str = valid_zone.name
        self.x: int = valid_zone.x
        self.y: int = valid_zone.y
        self.zone_type: ZoneTypes = valid_zone.zone_type
        self.max_drones: int = valid_zone.max_drones
        self.color: Union[str, tuple, None] = valid_zone.color
        self.current_drones: int = valid_zone.current_drones
        self.target_zone: Zone = []
