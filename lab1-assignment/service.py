import socket
import time
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Lab 1 Assignment Service")

START_TIME = time.monotonic()


@app.get("/info")
def info(delay: float = 0.0):
    if delay > 0:
        time.sleep(delay)
    return {
        "host": socket.gethostname(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health(delay: float = 0.0):
   
    if delay > 0:
        time.sleep(delay)
    uptime = time.monotonic() - START_TIME
    return {"status": "ok", "uptime_seconds": round(uptime, 3)}
