from .Zone import Zone
from typing import List
from pydantic import (
    BaseModel, Field,  ConfigDict,
    model_validator
)
from pydantic_core import PydanticCustomError
from typing import Optional


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
    turns_until_arrival: Optional[int] = Field(
        0, ge=0, description="Turns until the drone arrives"
    )
    step_remaining: Optional[int] = Field(
        0, ge=0, description="Remaining steps of the drone"
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
        self, id: str, current_zone: Zone, target_zone: Zone,
        turns_until_arrival: Optional[int] = 0,
        step_remaining: Optional[int] = 0
    ) -> None:
        self.id: str = id
        self.current_zone: Zone = current_zone
        self.target_zone: Zone = target_zone
        self.turns_until_arrival: int = turns_until_arrival
        self.step_remaining: int = step_remaining
