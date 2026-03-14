from os import environ
from pydantic import (
    BaseModel, Field, field_validator
)
from pydantic_core import PydanticCustomError
from enum import Enum
from typing import Optional, Union, List, Dict, Tuple

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from pygame.colordict import THECOLORS # noqa


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
        description="X of zone's coordinate"
    )
    y: int = Field(
        description="Y of zone's coordinate"
    )
    zone_type: Optional[ZoneTypes] = Field(
        ZoneTypes.NORMAL,
        description="Type of the zone, default normal"
    )
    color: Optional[Union[str, None]] = Field(
        None, min_length=3, description="Color of the zone"
    )
    max_drones: Optional[int] = Field(
        1, ge=1,
        description="Maximum drones that can occupy this zone simultaneously"
    )

    @field_validator('color', mode="after")
    def initialize_color(cls, color: str) -> tuple | str | None:
        if isinstance(color, tuple):
            return color

        color_tuple: tuple | str | None = color
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
        max_drones: Optional[int] = 1, color: Optional[str] = ""
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: ZoneTypes | None = zone_type
        self.max_drones: int | None = max_drones
        self.color: Tuple[int, int, int, int] | str | None = color
        self.target_zone: List[Zone] = []
        self.contain_zones: int = 0
        self.g: int = self.get_cost(self.zone_type)
        self.h: float = float("inf")
        self.f: float = float("inf")

    def get_cost(self, zone_type: ZoneTypes | None) -> int:
        if not zone_type:
            return 0
        cost_zones: Dict[ZoneTypes, int] = {
            ZoneTypes.NORMAL: 1,
            ZoneTypes.RESTRICTED: 2,
            ZoneTypes.PRIORITY: 1,
            ZoneTypes.BLOCKED: 0,
        }
        return cost_zones.get(zone_type, 0)
