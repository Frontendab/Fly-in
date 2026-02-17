from .Zone import Zone
from pydantic import BaseModel, Field,  ConfigDict


class ValidateDrone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int = Field(
        1, ge=0, description="ID of the drone"
    )
    current_zone: Zone = Field(
        description="Current zone of the drone"
    )
    target_zone: Zone = Field(
        description="Target zone of the drone"
    )
    turns_until_arrival: int = Field(
        0, ge=0, description="Turns until the drone arrives"
    )
    step_remaining: int = Field(
        0, ge=0, description="Remaining steps of the drone"
    )


class Drone:
    def __init__(
        self, id: int, current_zone: Zone, target_zone: Zone,
        turns_until_arrival: int, step_remaining: int
    ) -> None:
        valid_drone = ValidateDrone(
            id, current_zone, target_zone, turns_until_arrival,
            step_remaining
        )
        self.id: int = valid_drone.id
        self.current_zone: Zone = valid_drone.current_zone
        self.target_zone: Zone = valid_drone.target_zone
        self.turns_until_arrival: int = valid_drone.turns_until_arrival
        self.step_remaining: int = valid_drone.step_remaining
