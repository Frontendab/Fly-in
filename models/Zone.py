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
    """ZoneTypes: Is Enum class that contain const variables
        to use them in any part of project

    Args:
        Enum (_type_): It Enum class we inherits from it
            to be this class as enum's class
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ValidateZone(BaseModel):
    """ValidateZone is class to check if
        the Zone information is valid or not with raise errors

    Args:
        BaseModel: It inherits from BaseModel's pydantic to be
            validator's class
    """

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
        None, description="Color of the zone"
    )
    max_drones: Optional[int] = Field(
        1, ge=0,
        description="Maximum drones that can occupy this zone simultaneously"
    )

    @field_validator('color', mode="after")
    def initialize_color(cls, color: str) -> tuple | str | None:
        """initialize_color: Is used to convert
            the color's name to RGBA's format

        Args:
            color (str): Color's name

        Raises:
            PydanticCustomError: is used to raise custom pydantic's error

        Returns:
            tuple | str | None: Return the tuple of color's name,
                otherwise return(it or None)
        """
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
        """__init__ is use to assign values to the current instance
        """
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
        """get_cost: Is used to return the cost based on the zone's type

        Args:
            zone_type (ZoneTypes | None): Zone type you want it is cost

        Returns:
            int: Return the zone's cost if the type is supported,
                otherwise return 0
        """
        if not zone_type:
            return 0
        cost_zones: Dict[ZoneTypes, int] = {
            ZoneTypes.NORMAL: 1,
            ZoneTypes.RESTRICTED: 2,
            ZoneTypes.PRIORITY: 1,
            ZoneTypes.BLOCKED: 0,
        }
        return cost_zones.get(zone_type, 0)
