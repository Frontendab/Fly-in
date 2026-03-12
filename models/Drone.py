from .Zone import Zone
from typing import List
from pydantic import (
    BaseModel, Field,  ConfigDict,
    model_validator
)
from pydantic_core import PydanticCustomError


class ValidateDrone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(
        description="ID of the drone"
    )
    current_zone: Zone = Field(
        description="Current zone of the drone"
    )
    target_zone: List[Zone] = Field(
        description="Target zone of the drone"
    )

    @model_validator(mode="after")
    def check_valid_id(self) -> object:
        if not self.id.startswith("D"):
            raise PydanticCustomError(
                "invalid_color",
                (
                    "Invalid color name. " +
                    "See: https://www.pygame.org/docs/ref/color_list.html"
                )
            )

        return self


class Drone:
    def __init__(
        self, id: str, current_zone: Zone, target_zone: Zone
    ) -> None:
        self.id: str = id
        self.current_zone: Zone = current_zone
        self.target_zone: Zone = target_zone
        self.current_x: int = current_zone.x
        self.current_y: int = current_zone.y
        self.path: List[Zone] = []
        self.target_index = 0

    def get_x(self, viz: object) -> None:
        return (self.current_zone.x - viz.min_x) * viz.spacing + (
            viz.start_x + 35)

    def get_y(self, viz: object) -> None:
        return (self.current_zone.y - viz.min_y) * viz.spacing + (
            viz.start_y + 85)

    def set_pos(self, x: int, y: int) -> None:
        self.current_x = x
        self.current_y = y
