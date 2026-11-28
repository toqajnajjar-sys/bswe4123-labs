import asyncio
import os

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

app = FastAPI(title="Room Booking Service")

DELAY = float(os.getenv("ROOM_DELAY", "0"))

@app.middleware("http")
async def slow_down(request: Request, call_next):
    if DELAY > 0:
        await asyncio.sleep(DELAY)   
    return await call_next(request)

class Room(BaseModel):
    id: str
    capacity: int = Field(gt=0)

class Booking(BaseModel):
    room_id: str
    exam_id: str
    day: str
    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=1, le=24)

rooms: dict[str, Room] = {
    "R1": Room(id="R1", capacity=20),
    "R2": Room(id="R2", capacity=50),
    "R3": Room(id="R3", capacity=100),
    "R4": Room(id="R4", capacity=200),
}
bookings: list[Booking] = []

@app.get("/config")
def config():
    return {"delay_seconds": DELAY}

@app.get("/rooms")
def list_rooms():
    return list(rooms.values())

@app.post("/bookings", status_code=201)
def book(b: Booking):
    if b.room_id not in rooms:
        raise HTTPException(404, f"Room {b.room_id} not found")

    for existing in bookings:
        if existing.room_id == b.room_id and existing.day == b.day:
            overlap = not (b.end_hour <= existing.start_hour
                           or b.start_hour >= existing.end_hour)
            if overlap:
                raise HTTPException(409, "Room already booked at that time")
    bookings.append(b)
    return b