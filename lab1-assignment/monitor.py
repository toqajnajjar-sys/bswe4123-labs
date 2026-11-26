import time
import urllib.error
import urllib.request

SERVICES = [
    ("service-8001", "http://127.0.0.1:8001/health"),
    ("service-8002", "http://127.0.0.1:8002/health"),
    ("service-8003", "http://127.0.0.1:8003/health"),
]

INTERVAL = 2.0
TIMEOUT = 1.0
SLOW_THRESHOLD = 0.5
FAILURE_THRESHOLD = 3

failures = {name: 0 for name, _ in SERVICES}


def check(url: str):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
            response.read()
        elapsed = time.perf_counter() - start
        if elapsed > SLOW_THRESHOLD:
            return "SLOW", elapsed
        return "UP", elapsed
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return "DOWN", None


def main() -> None:
    print(f"Monitoring {len(SERVICES)} services every {INTERVAL}s")
    print(f"timeout={TIMEOUT}s | slow>{SLOW_THRESHOLD*1000:.0f}ms | "
          f"DOWN after {FAILURE_THRESHOLD} consecutive failures\n")
    round_no = 0
    try:
        while True:
            round_no += 1
            timestamp = time.strftime("%H:%M:%S")
            parts = []
            for name, url in SERVICES:
                state, elapsed = check(url)
                if state == "DOWN":
                    failures[name] += 1
                else:
                    failures[name] = 0

                if failures[name] >= FAILURE_THRESHOLD:
                    display = "DOWN"
                elif failures[name] > 0:
                    display = f"SUSPECT({failures[name]}/{FAILURE_THRESHOLD})"
                elif elapsed is None:
                    display = "UP"
                else:
                    display = f"{state} ({elapsed*1000:.0f} ms)"

                parts.append(f"{name}={display}")
            print(f"[{timestamp}] round {round_no}: " + " | ".join(parts))
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
