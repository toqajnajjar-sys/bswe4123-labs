import os
import time

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOMS_URL = os.getenv("ROOMS_URL", "http://localhost:8001")
TIMEOUT = float(os.getenv("ROOMS_TIMEOUT", "2.0"))
MAX_RETRIES = int(os.getenv("ROOMS_MAX_RETRIES", "3"))
BACKOFF_BASE = float(os.getenv("ROOMS_BACKOFF_BASE", "0.5"))

app = FastAPI(title="Exam Scheduler Service")

rooms_api = httpx.Client(base_url=ROOMS_URL, timeout=TIMEOUT)

class ExamRequest(BaseModel):
    exam_id: str = Field(min_length=1, examples=["E-001"])
    course_code: str = Field(examples=["BSWE4321"])
    day: str = Field(examples=["2025-06-10"])
    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=1, le=24)
    students: int = Field(gt=0)


booked_exams: dict[str, dict] = {}

def _call_with_retry(method: str, path: str, **kwargs):
    """Call Room Booking Service with retries + exponential backoff.

    Retry on: timeout, connection error, 5xx.
    Do NOT retry on: 404, 409 (permanent client errors).
    """
    last_exc = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            reply = rooms_api.request(method, path, **kwargs)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            last_exc = exc
        else:
            if 500 <= reply.status_code < 600:
                last_exc = HTTPException(503, "Room Booking Service returned 5xx")
            elif reply.status_code in (404, 409):
                return reply           
            else:
                return reply           
        if attempt < MAX_RETRIES:
            wait = BACKOFF_BASE * (2 ** attempt)  
            print(f"[retry] attempt {attempt+1} failed, sleeping {wait}s")
            time.sleep(wait)
    
    if isinstance(last_exc, httpx.TimeoutException):
        raise HTTPException(504, "Room Booking Service timed out")
    if isinstance(last_exc, httpx.ConnectError):
        raise HTTPException(503, "Room Booking Service unreachable")
    raise HTTPException(503, "Room Booking Service failed after retries")

@app.get("/config")
def config():
    return {
        "rooms_url": ROOMS_URL,
        "timeout_seconds": TIMEOUT,
        "max_retries": MAX_RETRIES,
        "backoff_base_seconds": BACKOFF_BASE,
    }

@app.post("/exams", status_code=201)
def schedule_exam(exam: ExamRequest):
    
    if exam.exam_id in booked_exams:
        return booked_exams[exam.exam_id]

    rooms_reply = _call_with_retry("GET", "/rooms")
    if rooms_reply.status_code != 200:
        raise HTTPException(503, "Could not fetch rooms")
    rooms = rooms_reply.json()

    candidates = sorted(
        [r for r in rooms if r["capacity"] >= exam.students],
        key=lambda r: r["capacity"],
    )
    if not candidates:
        raise HTTPException(409, "No free room large enough")

    for room in candidates:
        payload = {
            "room_id": room["id"],
            "exam_id": exam.exam_id,
            "day": exam.day,
            "start_hour": exam.start_hour,
            "end_hour": exam.end_hour,
        }
        reply = _call_with_retry("POST", "/bookings", json=payload)
        if reply.status_code == 201:
            booked_exams[exam.exam_id] = reply.json()
            return reply.json()
        if reply.status_code == 409:
            continue          
        continue

    raise HTTPException(409, "No free room large enough at that time")