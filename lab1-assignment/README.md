# Lab Assignment 1 — Is the Service Up, Slow or Down?

This folder contains `service.py` (with `/health`), `monitor.py`
(checks three services every 2 s), and `service_slow.py` (a slow copy
used in step 3).

## Step 3 — Monitor output
Monitoring 3 services every 2.0s (timeout=1.0s, slow threshold=500 ms)
[16:36:44] round 1: service-8001=UP (47 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:36:46] round 2: service-8001=UP (3 ms) | service-8002=UP (4 ms) | service-8003=UP (3 ms)
[16:36:48] round 3: service-8001=UP (4 ms) | service-8002=UP (3 ms) | service-8003=UP (15 ms)
[16:36:50] round 4: service-8001=UP (9 ms) | service-8002=UP (6 ms) | service-8003=UP (7 ms)
[16:36:52] round 5: service-8001=UP (5 ms) | service-8002=UP (5 ms) | service-8003=UP (7 ms)
[16:36:54] round 6: service-8001=UP (9 ms) | service-8002=UP (8 ms) | service-8003=UP (6 ms)
[16:36:56] round 7: service-8001=UP (8 ms) | service-8002=UP (7 ms) | service-8003=UP (9 ms)
[16:36:58] round 8: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:37:00] round 9: service-8001=UP (4 ms) | service-8002=UP (4 ms) | service-8003=UP (5 ms)
[16:37:02] round 10: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:37:04] round 11: service-8001=UP (3 ms) | service-8002=UP (5 ms) | service-8003=UP (3 ms)
[16:37:06] round 12: service-8001=UP (7 ms) | service-8002=UP (3 ms) | service-8003=UP (10 ms)
[16:37:08] round 13: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:37:10] round 14: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:37:12] round 15: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:37:14] round 16: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:37:16] round 17: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:37:18] round 18: service-8001=UP (4 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:37:20] round 19: service-8001=UP (3 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:37:22] round 20: service-8001=UP (5 ms) | service-8002=UP (5 ms) | service-8003=UP (7 ms)
[16:37:24] round 21: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (15 ms)
[16:37:26] round 22: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:37:28] round 23: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:37:30] round 24: service-8001=UP (3 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:37:32] round 25: service-8001=UP (13 ms) | service-8002=UP (16 ms) | service-8003=UP (6 ms)
[16:37:34] round 26: service-8001=UP (8 ms) | service-8002=UP (7 ms) | service-8003=UP (10 ms)
[16:37:36] round 27: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:37:38] round 28: service-8001=UP (11 ms) | service-8002=UP (11 ms) | service-8003=UP (12 ms)
[16:37:40] round 29: service-8001=UP (12 ms) | service-8002=UP (16 ms) | service-8003=UP (15 ms)
[16:37:42] round 30: service-8001=UP (6 ms) | service-8002=UP (6 ms) | service-8003=UP (6 ms)
[16:37:44] round 31: service-8001=UP (10 ms) | service-8002=UP (12 ms) | service-8003=UP (11 ms)
[16:37:46] round 32: service-8001=UP (5 ms) | service-8002=UP (4 ms) | service-8003=UP (7 ms)
[16:37:48] round 33: service-8001=UP (10 ms) | service-8002=UP (10 ms) | service-8003=UP (8 ms)
[16:37:51] round 34: service-8001=UP (5 ms) | service-8002=UP (4 ms) | service-8003=UP (6 ms)
[16:37:53] round 35: service-8001=UP (10 ms) | service-8002=UP (9 ms) | service-8003=UP (12 ms)
[16:37:55] round 36: service-8001=UP (2 ms) | service-8002=UP (3 ms) | service-8003=UP (4 ms)
[16:37:57] round 37: service-8001=UP (2 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:37:59] round 38: service-8001=UP (3 ms) | service-8002=UP (3 ms) | service-8003=UP (4 ms)
[16:38:01] round 39: service-8001=UP (3 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:38:03] round 40: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (4 ms)
[16:38:05] round 41: service-8001=UP (3 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:38:07] round 42: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:38:09] round 43: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:38:11] round 44: service-8001=UP (27 ms) | service-8002=UP (3 ms) | service-8003=UP (3 ms)
[16:38:13] round 45: service-8001=UP (6 ms) | service-8002=UP (12 ms) | service-8003=UP (8 ms)
[16:38:15] round 46: service-8001=UP (5 ms) | service-8002=UP (3 ms) | service-8003=UP (4 ms)
[16:38:17] round 47: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (6 ms)
[16:38:19] round 48: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:38:21] round 49: service-8001=UP (5 ms) | service-8002=UP (5 ms) | service-8003=UP (6 ms)
[16:38:23] round 50: service-8001=UP (7 ms) | service-8002=UP (4 ms) | service-8003=UP (3 ms)
[16:38:25] round 51: service-8001=UP (4 ms) | service-8002=UP (5 ms) | service-8003=UP (5 ms)
[16:38:27] round 52: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (6 ms)
[16:38:29] round 53: service-8001=UP (10 ms) | service-8002=UP (9 ms) | service-8003=UP (9 ms)
[16:38:31] round 54: service-8001=UP (2 ms) | service-8002=UP (3 ms) | service-8003=UP (5 ms)
[16:38:33] round 55: service-8001=UP (2 ms) | service-8002=UP (23 ms) | service-8003=UP (2 ms)
[16:38:35] round 56: service-8001=UP (2 ms) | service-8002=UP (2 ms) | service-8003=UP (2 ms)
[16:38:37] round 57: service-8001=UP (7 ms) | service-8002=UP (7 ms) | service-8003=UP (8 ms)
[16:38:39] round 58: service-8001=UP (3 ms) | service-8002=UP (2 ms) | service-8003=UP (3 ms)
[16:38:41] round 59: service-8001=UP (7 ms) | service-8002=UP (7 ms) | service-8003=UP (8 ms)
[16:38:43] round 60: service-8001=UP (9 ms) | service-8002=UP (6 ms) | service-8003=UP (11 ms)



### Explanation of changes

All three services stayed UP during the recorded minute because none
was stopped or slowed down. Response times were between 2 and 47 ms,
below the 500 ms threshold.

- If a service is stopped: the monitor prints DOWN (or SUSPECT(1/3)).
- If a service is slow (0.8 s): it prints SLOW (~804 ms).
- When restarted: it goes back to UP.

## Step 4 — Timeout and failure threshold

I chose timeout = 1.0 s and 3 consecutive failures.

- Gain: transient failures do not trigger a false DOWN alarm.
- Cost: detection takes about 6 s (worst case 9 s) instead of 2 s.
'@ | Set-Content -Path README.md -Encoding UTF8
