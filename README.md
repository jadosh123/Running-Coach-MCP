# running-coach

An MCP server that gives Claude (or any MCP client) access to your Garmin running data.

## Status

The core loop works end-to-end: Garmin login, sync, and local storage, plus an MCP server exposing tools to read activities and splits, read/write notes, and build and push structured workouts (cadence, heart rate, and pace targets) to a Garmin device. CI and packaging for one-click install are still outstanding.

## What it does

Syncs your Garmin running activities into a local SQLite database, including per-activity summaries and per-lap splits (1 km by default, depending on your watch's auto-lap setting). It also has a notes table for free-text observations, such as pains or how a run felt. The MCP server exposes tools so an LLM can look up runs, read and write notes, analyze trends over time, and build and push structured workouts — cadence, heart rate, or pace targets — to your Garmin device.

Everything runs locally. Your data stays on your machine, and your Garmin password is never stored.

## Architecture

```
Garmin Connect
      |
      v
sync (garminconnect)  ->  local SQLite DB  <-  MCP server  <-  Claude
      ^                                            |
      |                                            v
garmin-auth (one-time login, caches tokens)    workout_builder  ->  Garmin Connect (upload + push to device)
```

- `garmin.py`: interactive login (`garmin-auth`) and `get_client()`, which loads the cached tokens without prompting.
- `sync.py`: fetches new activities and splits since the last stored run and writes them to the DB.
- `db.py`: SQLite access. Schema versioning uses `PRAGMA user_version`, and migrations run automatically on connect.
- `models.py`: Pydantic schemas for activities, splits, and typed workout goals (cadence/heart rate/pace).
- `workout_builder.py`: turns typed workout goals into a `garminconnect` `RunningWorkout` ready to upload.
- `paths.py`: where the data lives.
- `server.py`: the MCP server.

## Tools

| Tool | Status | Description |
| --- | --- | --- |
| `sync_activities` | Done | Fetch new runs from Garmin into the local DB |
| `get_recent_activities` | Done | List the most recent runs |
| `get_activity` | Done | Fetch one activity by id |
| `get_activity_splits` | Done | Per-lap splits for one run |
| `get_activity_notes` / `get_recent_notes` | Done | Read notes for a run, or the newest notes overall |
| `write_note` / `delete_note` | Done | Write and delete notes |
| `upload_running_workout` | Done | Build and upload a structured workout (cadence, heart rate, or pace targets) to Garmin Connect |
| `push_workout_to_watch` | Done | Push an uploaded workout straight to the connected device, bypassing the calendar |

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync

# 1. Log in once (prompts for email, password, and MFA code if enabled).
#    Tokens are cached in ~/.garminconnect; the password is not stored.
uv run garmin-auth

# 2. Pull your runs into the local database or prompt claude code after the setup (Theres a tool for syncing).
uv run python -m running_coach.sync
```

After the first login, syncing needs no credentials. You only need to log in again if the cached tokens expire.

### Connecting to Claude

With Claude Code, from this repo's directory:

```bash
claude mcp add running-coach -- uv run running-coach
```

Claude Desktop isn't supported yet — see Roadmap.

The database lives in your OS's per-user app-data folder (for example `~/.local/share/running-coach/` on Linux). Set `RUNNING_COACH_DATA_DIR` to use a different folder.


## Roadmap

- Package as an `.mcpb` bundle for one-click install in Claude Desktop
- Schedule a workout onto a specific calendar date (`schedule_workout`), not just push it straight to the device
- Consolidate old notes into summaries for long-term context
- Fallback ingestion from Garmin's manual data export (`.FIT` files)
