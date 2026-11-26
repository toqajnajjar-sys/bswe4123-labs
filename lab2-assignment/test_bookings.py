"""الواجب الثاني - نجرّب كل حالات النجاح والخطأ في خدمة الحجز.

الاستخدام: python test_bookings.py http://localhost:8000
"""
import sys
import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
failures = 0

def show(label, response, expected):
    global failures
    ok = response.status_code == expected
    failures += 0 if ok else 1
    body = response.text if response.content else "(no body)"
    mark = "OK " if ok else "FAIL"
    print(f"[{mark}] {label:<52} -> {response.status_code} (expected {expected})  {body}")

with httpx.Client(base_url=base, timeout=5.0) as c:
    show("POST /rooms B205", c.post("/rooms", json={"id": "B205", "building": "Engineering", "capacity": 40}), 201)
    show("POST /rooms A101", c.post("/rooms", json={"id": "A101", "building": "Science", "capacity": 2}), 201)
    show("POST /rooms B205 again (duplicate)", c.post("/rooms", json={"id": "B205", "building": "Engineering", "capacity": 40}), 409)
    show("POST /rooms invalid capacity", c.post("/rooms", json={"id": "C1", "building": "Arts", "capacity": 0}), 422)
    show("GET /rooms", c.get("/rooms"), 200)
    show("GET /rooms/B205", c.get("/rooms/B205"), 200)
    show("GET /rooms/ZZZ", c.get("/rooms/ZZZ"), 404)

    b1 = {"room_id": "B205", "day": "2026-03-10", "start_hour": 10, "end_hour": 12, "purpose": "Study group"}
    b2 = {"room_id": "B205", "day": "2026-03-10", "start_hour": 12, "end_hour": 13, "purpose": "Meeting"}
    show("PUT /bookings/bk1 (10-12)", c.put("/bookings/bk1", json=b1), 201)
    show("PUT /bookings/bk2 (12-13, touching)", c.put("/bookings/bk2", json=b2), 201)
    show("GET /bookings/bk1", c.get("/bookings/bk1"), 200)
    show("GET /bookings?room_id=B205&day=2026-03-10", c.get("/bookings", params={"room_id": "B205", "day": "2026-03-10"}), 200)

    b3 = {"room_id": "B205", "day": "2026-03-10", "start_hour": 11, "end_hour": 13, "purpose": "Overlap"}
    show("PUT /bookings/bk3 (11-13 overlaps)", c.put("/bookings/bk3", json=b3), 409)
    bad = {"room_id": "B205", "day": "2026-03-10", "start_hour": 14, "end_hour": 9, "purpose": "Bad"}
    show("PUT /bookings/bk4 (end before start)", c.put("/bookings/bk4", json=bad), 422)
    oob = {"room_id": "B205", "day": "2026-03-10", "start_hour": 7, "end_hour": 9, "purpose": "Early"}
    show("PUT /bookings/bk5 (hour 7 out of range)", c.put("/bookings/bk5", json=oob), 422)
    unknown = {"room_id": "ZZZ", "day": "2026-03-10", "start_hour": 9, "end_hour": 10, "purpose": "Ghost"}
    show("PUT /bookings/bk6 (unknown room)", c.put("/bookings/bk6", json=unknown), 404)
    show("GET /bookings/nope", c.get("/bookings/nope"), 404)

    show("PUT /bookings/bk1 again (identical retry)", c.put("/bookings/bk1", json=b1), 200)
    changed = dict(b1, purpose="Something else")
    show("PUT /bookings/bk1 (same id, new body)", c.put("/bookings/bk1", json=changed), 409)
    show("GET /bookings (still 2 for B205)", c.get("/bookings"), 200)

    show("DELETE /bookings/bk2", c.delete("/bookings/bk2"), 204)
    show("DELETE /bookings/bk2 again", c.delete("/bookings/bk2"), 404)
    show("DELETE /rooms/A101", c.delete("/rooms/A101"), 204)
    show("GET /rooms/A101", c.get("/rooms/A101"), 404)

print(f"\n{failures} unexpected status code(s).")
sys.exit(1 if failures else 0)