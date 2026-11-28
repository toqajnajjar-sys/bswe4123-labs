import time
import httpx

EXAM = {
    "exam_id": "E-100",
    "course_code": "BSWE4321",
    "day": "2025-06-15",
    "start_hour": 9,
    "end_hour": 11,
    "students": 30,
}

SCHED = "http://localhost:8002"

def timed_post(label):
    t0 = time.perf_counter()
    try:
        r = httpx.post(f"{SCHED}/exams", json=EXAM, timeout=30.0)
        dt = time.perf_counter() - t0
        print(f"{label}: status={r.status_code}  time={dt:.2f}s  body={r.text[:120]}")
    except httpx.HTTPError as e:
        dt = time.perf_counter() - t0
        print(f"{label}: EXCEPTION {type(e).__name__}  time={dt:.2f}s")

print("=== Step 1: first booking (Room Service UP) ===")
timed_post("first ")

print("\n=== Step 2: same exam again (idempotent) ===")
timed_post("second")

print("\n=== Step 3: Room Service DOWN (stop it now, then press Enter) ===")
input("Press Enter when Room Booking Service is stopped... ")
timed_post("down  ")

print("\n=== Step 4: Room Service UP again (restart it, then press Enter) ===")
input("Press Enter when Room Booking Service is running... ")
timed_post("up    ")