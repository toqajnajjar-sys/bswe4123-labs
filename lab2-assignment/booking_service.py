"""الواجب الثاني - خدمة REST لحجز قاعات الحرم الجامعي."""
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Campus Room Booking Service")


class Room(BaseModel):
    """قاعة قابلة للحجز. المعرف id هو عنوان المورد، مثلاً B205."""
    id: str = Field(min_length=2, max_length=10, examples=["B205"])
    building: str = Field(min_length=2, examples=["Engineering"])
    capacity: int = Field(ge=1, le=500, examples=[40])

class Booking(BaseModel):
    """حجز قاعة واحدة في يوم واحد من ساعة البداية إلى ساعة النهاية.

    الساعات أعداد صحيحة بين 8 و20. الفترة نصف مفتوحة: [البداية, النهاية).
    """
    room_id: str = Field(min_length=2, max_length=10, examples=["B205"])
    day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-03-10"])
    start_hour: int = Field(ge=8, le=19, examples=[10])
    end_hour: int = Field(ge=9, le=20, examples=[12])
    purpose: str = Field(min_length=3, max_length=200, examples=["Study group"])

    @model_validator(mode="after")
    def check_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self

    def overlaps(self, other: "Booking") -> bool:
        """فترتان نصف مفتوحتان تتداخلان إذا كل وحدة تبدأ قبل ما تنتهي الثانية."""
        return (self.room_id == other.room_id
                and self.day == other.day
                and self.start_hour < other.end_hour
                and other.start_hour < self.end_hour)


rooms: dict[str, Room] = {}
bookings: dict[str, Booking] = {}   # المفتاح: رقم الحجز اللي يختاره العميل


@app.get("/rooms")
def list_rooms() -> list[Room]:
    return list(rooms.values())

@app.get("/rooms/{room_id}")
def get_room(room_id: str) -> Room:
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return rooms[room_id]

@app.post("/rooms", status_code=201)
def create_room(room: Room) -> Room:
    if room.id in rooms:
        raise HTTPException(status_code=409, detail=f"Room {room.id} already exists")
    rooms[room.id] = room
    return room

@app.delete("/rooms/{room_id}", status_code=204)
def delete_room(room_id: str) -> Response:
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    del rooms[room_id]
    for bid in [b for b, bk in bookings.items() if bk.room_id == room_id]:
        del bookings[bid]
    return Response(status_code=204)


@app.get("/bookings")
def list_bookings(room_id: str | None = None, day: str | None = None) -> list[Booking]:
    if room_id is not None and room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    result = list(bookings.values())
    if room_id is not None:
        result = [b for b in result if b.room_id == room_id]
    if day is not None:
        result = [b for b in result if b.day == day]
    return result

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str) -> Booking:
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return bookings[booking_id]

@app.put("/bookings/{booking_id}")
def put_booking(booking_id: str, booking: Booking) -> Response:
    """إنشاء/استبدال آمن للإعادة: نفس الطلب يرجع 200 وما ينشئ حجز جديد."""
    if booking.room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {booking.room_id} not found")

    existing = bookings.get(booking_id)

    if existing is not None and existing == booking:
        return Response(status_code=200)

    if existing is not None and existing != booking:
        raise HTTPException(
            status_code=409,
            detail=f"Booking {booking_id} already exists with different content",
        )

    for other_id, other in bookings.items():
        if other_id != booking_id and booking.overlaps(other):
            raise HTTPException(
                status_code=409,
                detail=(f"Room {booking.room_id} is already booked on {booking.day} "
                        f"from {other.start_hour} to {other.end_hour} (booking {other_id})"),
            )

    bookings[booking_id] = booking
    return Response(status_code=201)

@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str) -> Response:
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    del bookings[booking_id]
    return Response(status_code=204)