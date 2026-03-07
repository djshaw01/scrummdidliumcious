"""Performance integration test for the home landing page endpoint.

Requirement trace: SC-PERF — GET / p95 response time must be <= 300ms in local
containerized environment.
"""

import statistics
import time

SAMPLE_COUNT = 20
P95_THRESHOLD_MS = 300


def test_get_home_p95_response_time_under_300ms(client):
    """p95 response time for GET / must be <= 300ms (local in-process measurement).

    This test measures only Flask/Python processing time (excludes network
    round-trip latency) which is the appropriate scope for a unit-level
    performance gate against a local test client.

    :param client: Flask test client fixture.
    """
    durations_ms: list[float] = []

    for _ in range(SAMPLE_COUNT):
        start = time.perf_counter()
        response = client.get("/")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200, "GET / must return 200 for timing sample"
        durations_ms.append(elapsed_ms)

    durations_ms.sort()
    p95_index = int(len(durations_ms) * 0.95) - 1
    p95_ms = durations_ms[max(p95_index, 0)]

    assert p95_ms <= P95_THRESHOLD_MS, (
        f"GET / p95 response time {p95_ms:.1f}ms exceeds threshold of "
        f"{P95_THRESHOLD_MS}ms. "
        f"Samples: min={min(durations_ms):.1f}ms, "
        f"median={statistics.median(durations_ms):.1f}ms, "
        f"p95={p95_ms:.1f}ms, "
        f"max={max(durations_ms):.1f}ms"
    )
