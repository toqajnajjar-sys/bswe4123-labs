"""A copy of the service whose /health always waits 0.8 seconds."""
import time
from fastapi import FastAPI

app = FastAPI(title="Slow Service")
START_TIME = time.monotonic()

@app.get("/health")
def health():
    time.sleep(0.8)
    return {"status": "ok", "uptime_seconds": round(time.monotonic() - START_TIME, 3)}
