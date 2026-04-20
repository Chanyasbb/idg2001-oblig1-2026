"""Logger service — logs requests to date-rotated CSV files in a Docker volume.

Endpoints:
    POST /log       — log a single request (called by Main API on every request)
    POST /retention — update how many days of logs to keep
"""

import csv
import os
import time
from datetime import datetime, timedelta
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Logger Service")

LOG_DIR = os.getenv("LOG_DIR", "/logs")  # mounted as a Docker volume
_buffer: list[dict] = []                 # in-memory buffer before writing to CSV
_retention_days = 7                      # default: keep 7 days of logs


class LogEntry(BaseModel):
    username: str
    endpoint: str


class RetentionUpdate(BaseModel):
    n: int  # number of days to keep


def _get_log_path(date_str: str) -> str:
    return os.path.join(LOG_DIR, f"log_{date_str}.csv")


def _flush_buffer() -> None:
    """Write buffered log entries to today's CSV file."""
    if not _buffer:
        return

    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = _get_log_path(date_str)
    file_exists = os.path.exists(path)

    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "username", "endpoint"])
        if not file_exists:
            writer.writeheader()  # add header on new files
        writer.writerows(_buffer)

    _buffer.clear()


def _delete_old_logs() -> None:
    """Remove log files older than retention_days.

    Expects filenames in the form log_YYYY-MM-DD.csv (as produced by _get_log_path).
    """
    if not os.path.exists(LOG_DIR):
        return
    cutoff = datetime.now() - timedelta(days=_retention_days)
    for filename in os.listdir(LOG_DIR):
        if not filename.startswith("log_") or not filename.endswith(".csv"):
            continue
        date_str = filename[4:14]  # "log_YYYY-MM-DD.csv" → "YYYY-MM-DD"
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        if file_date < cutoff:
            os.remove(os.path.join(LOG_DIR, filename))


@app.post("/log")
def log_request(entry: LogEntry):
    """Buffer a log entry. Flushes to CSV when buffer is big enough (or on new day)."""
    _buffer.append({
        "time": datetime.now().isoformat(),
        "username": entry.username,
        "endpoint": entry.endpoint,
    })
    # TODO: flush when buffer reaches N entries, or when the date changes
    _flush_buffer()
    return {"logged": True}


@app.post("/retention")
def set_retention(body: RetentionUpdate):
    """Override how many days of logs to keep."""
    global _retention_days
    _retention_days = body.n
    _delete_old_logs()
    return {"retention_days": _retention_days}
