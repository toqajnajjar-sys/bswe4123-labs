# Lab Assignment 2 – Campus Room Booking Service

**Name:** Toqa Jehad Al Najjar
**Repository folder:** `lab2-assignment`

## 1. API Design

| # | Operation | Method | URI | Request body | Success | Error codes |
|---|-----------|--------|-----|--------------|---------|-------------|
| 1 | List rooms | GET | `/rooms` | – | 200 | – |
| 2 | Get one room | GET | `/rooms/{room_id}` | – | 200 | 404 unknown room |
| 3 | Create a room | POST | `/rooms` | `Room` (id, building, capacity) | 201 | 409 duplicate id, 422 invalid data |
| 4 | Delete a room | DELETE | `/rooms/{room_id}` | – | 204 | 404 unknown room |
| 5 | List bookings (with optional filters) | GET | `/bookings?room_id=&day=` | – | 200 | 404 if filter refers to unknown room |
| 6 | Get one booking | GET | `/bookings/{booking_id}` | – | 200 | 404 unknown booking |
| 7 | Create/replace a booking (safe to retry) | PUT | `/bookings/{booking_id}` | `Booking` (room_id, day, start_hour, end_hour, purpose) | 201 first time, 200 identical retry | 404 unknown room, 409 overlap or conflicting retry, 422 invalid data |
| 8 | Delete a booking | DELETE | `/bookings/{booking_id}` | – | 204 | 404 unknown booking |

### Design notes

- **Overlap rule:** bookings are half-open intervals `[start_hour, end_hour)`. Two intervals overlap iff `start1 < end2 AND start2 < end1`. Touching intervals (10–12 and 12–13) do **not** overlap.
- **Hours:** whole hours between 8 and 20. `end_hour > start_hour` is enforced by a Pydantic `model_validator`, so violations return **422** with the field name and reason.
- **Invalid data:** Pydantic `Field` constraints (`ge`, `le`, `min_length`, `pattern`) reject bad requests with **422** automatically.
- **Retry safety:** the client chooses the booking id and sends it with `PUT`. Re-sending the same request returns 200 and creates nothing new. See Section 3.

## 2. Output of `test_bookings.py`

Command: `python test_bookings.py http://localhost:8000`
[OK ] POST /rooms B205 -> 201 (expected 201) {"id":"B205","building":"Engineering","capacity":40}
[OK ] POST /rooms A101 -> 201 (expected 201) {"id":"A101","building":"Science","capacity":2}
[OK ] POST /rooms B205 again (duplicate) -> 409 (expected 409) {"detail":"Room B205 already exists"}
[OK ] POST /rooms invalid capacity -> 422 (expected 422) {"detail":[{"type":"greater_than_equal","loc":["body","capacity"],"msg":"Input should be greater than or equal to 1","input":0,"ctx":{"ge":1}}]}
[OK ] GET /rooms -> 200 (expected 200) [{"id":"B205","building":"Engineering","capacity":40},{"id":"A101","building":"Science","capacity":2}]
[OK ] GET /rooms/B205 -> 200 (expected 200) {"id":"B205","building":"Engineering","capacity":40}
[OK ] GET /rooms/ZZZ -> 404 (expected 404) {"detail":"Room ZZZ not found"}
[OK ] PUT /bookings/bk1 (10-12) -> 201 (expected 201) (no body)
[OK ] PUT /bookings/bk2 (12-13, touching) -> 201 (expected 201) (no body)
[OK ] GET /bookings/bk1 -> 200 (expected 200) {"room_id":"B205","day":"2026-03-10","start_hour":10,"end_hour":12,"purpose":"Study group"}
[OK ] GET /bookings?room_id=B205&day=2026-03-10 -> 200 (expected 200) [{"room_id":"B205","day":"2026-03-10","start_hour":10,"end_hour":12,"purpose":"Study group"},{"room_id":"B205","day":"2026-03-10","start_hour":12,"end_hour":13,"purpose":"Meeting"}]
[OK ] PUT /bookings/bk3 (11-13 overlaps) -> 409 (expected 409) {"detail":"Room B205 is already booked on 2026-03-10 from 10 to 12 (booking bk1)"}
[OK ] PUT /bookings/bk4 (end before start) -> 422 (expected 422) {"detail":[{"type":"value_error","loc":["body"],"msg":"Value error, end_hour must be greater than start_hour","input":{"room_id":"B205","day":"2026-03-10","start_hour":14,"end_hour":9,"purpose":"Bad"},"ctx":{"error":{}}}]}
[OK ] PUT /bookings/bk5 (hour 7 out of range) -> 422 (expected 422) {"detail":[{"type":"greater_than_equal","loc":["body","start_hour"],"msg":"Input should be greater than or equal to 8","input":7,"ctx":{"ge":8}}]}
[OK ] PUT /bookings/bk6 (unknown room) -> 404 (expected 404) {"detail":"Room ZZZ not found"}
[OK ] GET /bookings/nope -> 404 (expected 404) {"detail":"Booking nope not found"}
[OK ] PUT /bookings/bk1 again (identical retry) -> 200 (expected 200) (no body)
[OK ] PUT /bookings/bk1 (same id, new body) -> 409 (expected 409) {"detail":"Booking bk1 already exists with different content"}
[OK ] GET /bookings (still 2 for B205) -> 200 (expected 200) [{"room_id":"B205","day":"2026-03-10","start_hour":10,"end_hour":12,"purpose":"Study group"},{"room_id":"B205","day":"2026-03-10","start_hour":12,"end_hour":13,"purpose":"Meeting"}]
[OK ] DELETE /bookings/bk2 -> 204 (expected 204) (no body)
[OK ] DELETE /bookings/bk2 again -> 404 (expected 404) {"detail":"Booking bk2 not found"}
[OK ] DELETE /rooms/A101 -> 204 (expected 204) (no body)
[OK ] GET /rooms/A101 -> 404 (expected 404) {"detail":"Room A101 not found"}

0 unexpected status code(s).

## 3. Retry safety (Step 4)

**Design.** A booking is created with `PUT /bookings/{booking_id}`, where the **client chooses the booking id** (for example a UUID generated once when the user taps "Book" and reused on every retry). The body carries the full booking. The server logic is:

1. If the id does not exist and no existing booking of the same room/day overlaps it → store it and return **201**.
2. If the id exists with **exactly the same content** → return **200** and change nothing. This is the lost-reply case: the app resends the same request, the server recognises it as the same resource, and no second booking is created.
3. If the id exists with **different content** → return **409**, because a retry must never silently overwrite a different booking.
4. If the id is new but overlaps an existing booking → return **409**, because the overlap rule still applies.

The client script demonstrates this: the first `PUT /bookings/bk1` returns 201, the identical retry returns **200**, the number of bookings for that room/day stays at two, and a same-id/different-body retry returns 409.

**Why this matters.** `PUT` is idempotent by definition: N identical requests leave the server in the same state as one. A `POST /bookings` with a server-generated id would create a second booking on every retry — unacceptable for a booking app (a room gets double-booked) and catastrophic for a payment (the customer is charged twice). Client-chosen ids plus `PUT` turn the retry into a harmless replay.

