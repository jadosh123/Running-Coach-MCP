from pydantic import BaseModel, Field
from typing import Literal


class Activity(BaseModel):
    activity_id: int
    activity_name: str | None
    activity_type: str
    start_time_local: str
    start_time_gmt: str
    distance_meters: float | None
    duration_seconds: float | None
    moving_duration_seconds: float | None
    elevation_gain_meters: float | None
    elevation_loss_meters: float | None
    average_speed_mps: float | None = Field(None, description="Average pace, meters per second")
    max_speed_mps: float | None = Field(None, description="Max pace, meters per second")
    calories: float | None
    average_hr: float | None
    max_hr: float | None
    average_cadence: float | None = Field(None, description="Average cadence, steps per minute")
    max_cadence: float | None = Field(None, description="Max cadence, steps per minute")
    steps: int | None


class ActivitySplit(BaseModel):
    id: int
    activity_id: int
    lap_index: int
    start_time_gmt: str
    distance_meters: float | None
    duration_seconds: float | None
    moving_duration_seconds: float | None
    elevation_gain_meters: float | None
    elevation_loss_meters: float | None
    average_speed_mps: float | None = Field(None, description="Average pace, meters per second")
    max_speed_mps: float | None = Field(None, description="Max pace, meters per second")
    calories: float | None
    average_hr: float | None
    max_hr: float | None
    average_cadence: float | None = Field(None, description="Average cadence, steps per minute")
    max_cadence: float | None = Field(None, description="Max cadence, steps per minute")
    stride_length_cm: float | None = Field(None, description="Average stride length, centimeters")
    start_latitude: float | None
    start_longitude: float | None
    end_latitude: float | None
    end_longitude: float | None


class DurationEnd(BaseModel):
    unit: Literal["duration"] = "duration"
    seconds: float = Field(description="Step duration, seconds")


class DistanceEnd(BaseModel):
    unit: Literal["distance"] = "distance"
    meters: float = Field(description="Step distance, meters")


StepEnd = DurationEnd | DistanceEnd


class CadenceGoal(BaseModel):
    kind: Literal["cadence"] = "cadence"
    end: StepEnd
    min_cadence: float = Field(description="Minimum cadence, steps per minute")
    max_cadence: float = Field(description="Maximum cadence, steps per minute")


class HeartRateGoal(BaseModel):
    kind: Literal["heart_rate"] = "heart_rate"
    end: StepEnd
    min_hr: float = Field(description="Minimum heart rate, bpm")
    max_hr: float = Field(description="Maximum heart rate, bpm")


class PaceGoal(BaseModel):
    kind: Literal["pace"] = "pace"
    end: StepEnd
    min_speed_mps: float = Field(description="Slower pace bound, meters per second")
    max_speed_mps: float = Field(description="Faster pace bound, meters per second")


WorkoutTarget = CadenceGoal | HeartRateGoal | PaceGoal