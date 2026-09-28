from pydantic import BaseModel, Field
from typing import Literal
from garminconnect.workout import RunningWorkout, WorkoutSegment, ExecutableStep, TargetType, StepType, ConditionType


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
StepEnd = DurationEnd | DistanceEnd


def _set_from_target(target: WorkoutTarget, step_order: int) -> ExecutableStep:
    match target:
        case CadenceGoal(end=end, min_cadence=lo, max_cadence=hi):
            target_type = {"workoutTargetTypeId": TargetType.CADENCE, "workoutTargetTypeKey": "cadence", "displayOrder": 3}
        case HeartRateGoal(end=end, min_hr=lo, max_hr=hi):
            target_type = {"workoutTargetTypeId": TargetType.HEART_RATE_ZONE, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4}
        case PaceGoal(end=end, min_speed_mps=lo, max_speed_mps=hi):
            target_type = {"workoutTargetTypeId": TargetType.PACE_ZONE, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6}

    match end:
        case DurationEnd(seconds=value):
            end_condition = {"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True}
        case DistanceEnd(meters=value):
            end_condition = {"conditionTypeId": ConditionType.DISTANCE, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True}

    return ExecutableStep(
        stepOrder=step_order,
        stepType={"stepTypeId": StepType.INTERVAL, "stepTypeKey": "interval", "displayOrder": 3},
        endCondition=end_condition,
        endConditionValue=value,
        targetType=target_type,
        targetValueOne=lo,
        targetValueTwo=hi,
    )