from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from running_coach import db
from running_coach.models import Activity, ActivitySplit, WorkoutTarget
from running_coach import sync
from running_coach.garmin import get_client
from running_coach.workout_builder import build_running_workout
from garminconnect.exceptions import GarminConnectConnectionError, GarminConnectTooManyRequestsError
from typing import Any

mcp = MCPServer("Running Coach")


@mcp.tool()
def push_workout_to_watch(workout_id: int) -> Any:
    """Push an already-uploaded workout straight to the connected watch,
    bypassing the calendar. Use the workoutId returned by
    upload_running_workout."""
    client = get_client()
    try:
        return client.push_workout_to_device(workout_id=workout_id)
    except GarminConnectConnectionError as e:
        raise ToolError(f"Garmin couldn't push the workout: {e}") from e


@mcp.tool()
def upload_running_workout(workout_name: str, targets: list[WorkoutTarget]):
    """Upload a structured running workout to Garmin Connect. Each item in
    targets is one ordered step with a cadence, heart rate, or pace goal,
    ending after a set duration or distance. Steps run in the order given.
    This only creates the workout in Garmin Connect; it does not schedule
    it onto a date. Returns the created workout's data, including its id."""
    client = get_client()
    workout = build_running_workout(workout_name, targets)
    try:
        return client.upload_running_workout(workout)
    except GarminConnectConnectionError as e:
        raise ToolError(f"Garmin rejected the workout: {e}. Check the target and end-condition values before retrying.") from e
    except GarminConnectTooManyRequestsError as e:
        raise ToolError("Garmin rate-limited this request. Wait a bit before retrying.") from e


@mcp.tool()
def get_recent_activities(limit: int = 5) -> list[Activity]:
    """Fetch most recent N activities with the limit argument."""
    with db.connection() as conn:
        rows = db.get_recent_activities(conn, limit)

    if not rows:
        raise ToolError("No activities in the database yet. Run the sync tool first to populate it.")
    return [Activity(**row) for row in rows]


@mcp.tool()
def sync_activities(start_date: str | None = None) -> int:
    """Sync running activities from Garmin into the local database.
    If start_date (YYYY-MM-DD) is omitted, syncs incrementally from the
    last stored activity, or from a default lookback window on first run.
    Returns the number of activities synced."""
    return sync.sync_activities(start_date)


@mcp.tool()
def get_activity(activity_id: int) -> Activity:
    """Fetch activity by ID."""
    with db.connection() as conn:
        res = db.get_activity(conn, activity_id)

    if not res:
        raise ToolError(f"No activity found for activity_id={activity_id}. Use get_recent_activities to find valid IDs.")
    return Activity(**res)


@mcp.tool()
def get_activity_splits(activity_id: int) -> list[ActivitySplit]:
    """Fetch per-lap splits (usually 1 km auto-laps) for an activity:
    pace, HR, cadence, stride length and elevation per lap."""
    with db.connection() as conn:
        activity = db.get_activity(conn, activity_id)
        res = db.get_activity_splits(conn, activity_id)

    if not activity:
        raise ToolError(f"No activity found for activity_id={activity_id}. Use get_recent_activities to find valid IDs.")
    if not res:
        raise ToolError(f"Activity {activity_id} exists but has no lap data. Use get_activity for its summary instead.")
    return [ActivitySplit(**row) for row in res]


@mcp.tool()
def get_activity_notes(activity_id: int | None) -> list[dict[str, Any]]:
    """Fetch notes for activity_id, oldest first. If activity_id is omitted,
    fetches general notes not attached to any activity. Returns [] if none."""
    with db.connection() as conn:
        return db.get_activity_notes(conn, activity_id)


@mcp.tool()
def write_note(note: str, activity_id: int | None = None) -> int:
    """Save a coaching note. Attach it to a run with activity_id, or omit it
    for a general note (e.g. a standing goal). Returns the new note's id."""
    with db.connection() as conn:
        if activity_id is not None and db.get_activity(conn, activity_id) is None:
            raise ToolError(f"No activity found for activity_id={activity_id}. Use get_recent_activities to find valid IDs.")
        return db.store_note(conn, note, activity_id)


@mcp.tool()
def delete_note(note_ids: list[int]) -> int:
    """Permanently delete notes by id (get ids from get_activity_notes).
    Returns how many were deleted; fewer than requested means some ids didn't exist.
    Confirm with the user before deleting notes they wrote."""
    with db.connection() as conn:
        return db.delete_notes(conn, note_ids)


@mcp.tool()
def get_recent_notes(limit: int = 5) -> list[dict[str, Any]]:
    """Fetch the most recent notes across all activities and general notes,
    newest first. Use this to recall goals and past observations when you
    don't know which activity they belong to. Returns [] if none."""
    with db.connection() as conn:
        return db.get_recent_notes(conn, limit)


if __name__ == "__main__":
    mcp.run()