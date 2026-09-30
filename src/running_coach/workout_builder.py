from running_coach.models import CadenceGoal, HeartRateGoal, PaceGoal, DurationEnd, DistanceEnd, WorkoutTarget, StepEnd
from garminconnect.workout import RunningWorkout, WorkoutSegment, ExecutableStep, TargetType, StepType, ConditionType


def _step_from_target(target: WorkoutTarget, step_order: int) -> ExecutableStep:
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


def _estimate_running_duration(targets: list[WorkoutTarget]) -> int:
    total_time = 0
    for target in targets:
        match target.end:
            case DurationEnd(seconds=value):
                total_time += int(value)
            case DistanceEnd(meters=value):
                total_time += int(value / 2.77)

    return total_time


def build_running_workout(workout_name: str, targets: list[WorkoutTarget]) -> RunningWorkout:
    """Builds a typed workout (RunningWorkout) for uploading to garmin-connect
    Args:
        workout_name: The workout name as a string.
        targets: A list of typed WorkoutTarget like (CadenceGoal, HeartRateGoal, PaceGoal).
    
    Returns:
        A populated RunningWorkout instance ready for uploading to garmin-connect.
    """
    steps = [_step_from_target(target, step_order=i + 1) for i, target in enumerate(targets)]
    segment = WorkoutSegment(
        segmentOrder=1,
        sportType={
            "sportTypeId": 1,
            "sportTypeKey": "running",
            "displayOrder": 1
        },
        workoutSteps=steps
    )
    return RunningWorkout(
        workoutName=workout_name,
        estimatedDurationInSecs=_estimate_running_duration(targets),
        workoutSegments=[segment],
    )