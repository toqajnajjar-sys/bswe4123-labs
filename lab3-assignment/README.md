# Lab Assignment 3 — Exam Scheduler Service

**Student:** Toqa Jehad Al Najjar — 120230070
**Course:** BSWE 4123 — Distributed Software Systems Laboratory

---

## 1. Services

| Service | Port | File |
|---|---|---|
| Room Booking Service | 8001 | `room_booking_service.py` |
| Exam Scheduler Service | 8002 | `exam_scheduler_service.py` |

---

## 2. How to run

### Terminal 1 — Room Booking Service

```powershell
cd bswe4123-labs\lab3-assignment
.\.venv\Scripts\Activate.ps1
uvicorn room_booking_service:app --port 8001
```

Optional delay (simulates a slow service):

```powershell
$env:ROOM_DELAY="0.5"
```

### Terminal 2 — Exam Scheduler Service

```powershell
cd bswe4123-labs\lab3-assignment
.\.venv\Scripts\Activate.ps1
uvicorn exam_scheduler_service:app --port 8002
```

Configuration via environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `ROOMS_URL` | `http://localhost:8001` | Address of Room Booking Service |
| `ROOMS_TIMEOUT` | `2.0` | Timeout per HTTP call (seconds) |
| `ROOMS_MAX_RETRIES` | `3` | Max retries after the first attempt |
| `ROOMS_BACKOFF_BASE` | `0.5` | Base of exponential backoff (seconds) |

Check with `GET http://localhost:8002/config`.

---

## 3. Endpoints

| Method | Path | Result |
|---|---|---|
| `GET` | `/config` | Shows configuration values |
| `POST` | `/exams` | **201** with booked room; **409** if no free room large enough; **503** if Room Booking Service unreachable; **504** if timeout after retries |

Example request:

```json
{
  "exam_id": "E-100",
  "course_code": "BSWE4321",
  "day": "2025-06-15",
  "start_hour": 9,
  "end_hour": 11,
  "students": 30
}
```

---

## 4. Why the booking request is safe to retry

Two things make retrying safe:

1. **`POST /bookings` rejects overlapping bookings with 409.**
   If the first request actually reached the Room Booking Service and created a
   booking, resending the same request will hit the time-conflict check and
   return **409** — no duplicate is created.

2. **`POST /exams` caches results by `exam_id`.**
   If the same exam is sent twice, the scheduler returns the already-booked
   room from memory without touching the Room Booking Service again.

Therefore, a retry after a timeout/connection error either:

- succeeds once (201), or
- returns 409 (already booked), or
- returns the cached answer.

**It never produces a double booking.**

We retry only on **timeout, connection error, or 5xx** — these are transient.
We do **not** retry **404** or **409** because they are permanent: retrying
cannot change the result and only wastes time.

---

## 5. Retry test log

Test scenario (`test_retry.py`): book an exam, re-send the same exam, stop the
Room Booking Service, send again, restart it, send again.

```
=== Step 1: first booking (Room Service UP) ===
first : status=201  time=5.57s  body={"room_id":"R2","exam_id":"E-100","day":"2025-06-15","start_hour":9,"end_hour":11}

=== Step 2: same exam again (idempotent) ===
second: status=201  time=3.62s  body={"room_id":"R2","exam_id":"E-100","day":"2025-06-15","start_hour":9,"end_hour":11}

=== Step 3: Room Service DOWN ===
down  : status=201  time=3.01s  body={"room_id":"R2","exam_id":"E-100","day":"2025-06-15","start_hour":9,"end_hour":11}

=== Step 4: Room Service UP again ===
up    : status=201  time=2.52s  body={"room_id":"R2","exam_id":"E-100","day":"2025-06-15","start_hour":9,"end_hour":11}
```

**What we learned from the log:**

- **Steps 1–2** confirm **idempotency**: the same `exam_id` returns the same
  room (R2, the smallest room that fits 30 students) on both calls.

- **Step 3** returned **201 instead of 503** because the scheduler found
  `exam_id = "E-100"` already in its cache (`booked_exams`) and answered from
  memory **without calling the Room Booking Service**. This is the intended
  idempotency behaviour, but it means this particular run did not exercise the
  failure path. To exercise the failure path, Step 3 should use a **new**
  `exam_id` (e.g., `E-200`) so the scheduler is forced to call the Room
  Booking Service.

- The slow times in Steps 1 and 2 are explained by a `ROOM_DELAY` value that
  was still set in the Room Booking Service's environment during the run
  (the middleware sleeps `DELAY` seconds before every response). With
  `ROOM_DELAY = 0`, times drop to ~0.01 s.

---

## 6. Delay × timeout table

Three combinations were prepared. The expected results, based on the retry
logic in `exam_scheduler_service.py` (`MAX_RETRIES = 3`, backoff 0.5, 1, 2 s),
are:

| # | ROOM_DELAY | ROOMS_TIMEOUT | Expected status | Expected time (s) |
|---|---|---|---|---|
| 1 | 0.2 | 2.0 | **201** | ~0.2 |
| 2 | 1.0 | 2.0 | **201** | ~1.0 |
| 3 | 3.0 | 1.0 | **504** | ~4.5 |

**Explanation of the trade-off:**

- **Combination 1 (delay 0.2 < timeout 2.0):** every call finishes well before
  the timeout; the request succeeds on the first attempt. Time ≈ delay.
- **Combination 2 (delay 1.0 < timeout 2.0):** still succeeds, but slower.
  The margin between delay and timeout is small, so any extra load could
  push the request into timeout.
- **Combination 3 (delay 3.0 > timeout 1.0):** every attempt times out after
  1 s. The scheduler retries three times with backoff 0.5 + 1 + 2 = 3.5 s,
  then gives up with **504**. Total time ≈ 1 + 3.5 = 4.5 s.

**The trade-off in one sentence:**

- **Short timeout** → fast failure, but may cut off slow-but-valid requests
  (false failure).
- **Long timeout** → fewer false failures, but users wait a long time when the
  service is dead.
- **Retry** helps when failures are **transient** (service restarting, brief
  5xx). It **hurts** when the failure is **sustained** (service permanently
  slow/down): it adds latency and load without changing the outcome. Keep
  `MAX_RETRIES` small and back off exponentially.

**Recommended for this system:**

- `ROOMS_TIMEOUT = 2.0` s (above normal response time, below user patience)
- `ROOMS_MAX_RETRIES = 3`
- `ROOMS_BACKOFF_BASE = 0.5` s

---

## 7. Note on data persistence

The Room Booking Service keeps bookings in memory. Restarting it (Ctrl+C then
`uvicorn` again) empties the bookings list, so after a restart the same exam can
be booked again into the same room. This is acceptable for the lab but would
require a database in production.

---

## 8. Files

```
lab3-assignment/
├── room_booking_service.py      # Room Booking Service (port 8001)
├── exam_scheduler_service.py    # Exam Scheduler Service (port 8002)
├── test_retry.py                # retry + idempotency demonstration
└── README.md                    # this file
```