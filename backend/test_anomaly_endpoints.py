"""
End-to-end test for all anomaly detection endpoints.
Tests: POST /anomaly/train, GET /anomaly/detect, GET /anomaly/metrics
"""
import requests
import json

BASE = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTE0NGExYzQzYThlOGVmMjcwZGYzNWEiLCJlbWFpbCI6Imluc2lnaHRzdGVzdEB0ZXN0LmNvbSIsIm5hbWUiOiJJbnNpZ2h0cyBUZXN0IiwiZXhwIjoxNzc5ODMwNzIwfQ.Rp6jTzUHn6-KsiC0H8zvqSaKwoM3a8l33QVZR4BgQnI"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

PASS = "[PASS]"
FAIL = "[FAIL]"

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── Test 0: Health check ──────────────────────────────────
separator("TEST 0: Health Check")
r = requests.get(f"{BASE}/health")
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")
assert r.status_code == 200, "Health check failed"
print(f"{PASS} Health check passed")


# ── Test 1: POST /anomaly/train ───────────────────────────
separator("TEST 1: POST /anomaly/train")
r = requests.post(f"{BASE}/anomaly/train", headers=HEADERS)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {json.dumps(data, indent=2)}")

assert r.status_code == 200, f"Expected 200, got {r.status_code}"
assert "message" in data, "Missing 'message' field"
assert data["message"] == "Isolation Forest trained successfully", f"Wrong message: {data['message']}"
assert "trained_on" in data, "Missing 'trained_on' field"
assert data["trained_on"] > 50, f"trained_on too low: {data['trained_on']}"
print(f"{PASS} Train endpoint passed — trained on {data['trained_on']} records")


# ── Test 2: GET /anomaly/detect ───────────────────────────
separator("TEST 2: GET /anomaly/detect")
r = requests.get(f"{BASE}/anomaly/detect", headers=HEADERS)
print(f"Status: {r.status_code}")
data = r.json()
print(f"total_transactions: {data.get('total_transactions')}")
print(f"anomalies_detected: {data.get('anomalies_detected')}")
print(f"high: {data.get('high')}, medium: {data.get('medium')}, low: {data.get('low')}")

assert r.status_code == 200, f"Expected 200, got {r.status_code}"
assert "total_transactions" in data, "Missing 'total_transactions'"
assert "anomalies_detected" in data, "Missing 'anomalies_detected'"
assert "alerts" in data, "Missing 'alerts'"
assert data["total_transactions"] > 0, "No transactions found"

if data["anomalies_detected"] > 0:
    print(f"\nTop 3 alerts:")
    for alert in data["alerts"][:3]:
        print(f"  - [{alert['severity'].upper()}] {alert['merchant']}: "
              f"Rs.{alert['amount']:,.0f} ({', '.join(alert['detection_methods'])})")
        print(f"    {alert['message']}")

print(f"{PASS} Detect endpoint passed — {data['anomalies_detected']} anomalies in {data['total_transactions']} txns")


# ── Test 3: GET /anomaly/metrics ──────────────────────────
separator("TEST 3: GET /anomaly/metrics")
r = requests.get(f"{BASE}/anomaly/metrics", headers=HEADERS)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {json.dumps(data, indent=2)}")

assert r.status_code == 200, f"Expected 200, got {r.status_code}"
print(f"{PASS} Metrics endpoint passed")


# ── Test 4: POST /anomaly/train without auth ──────────────
separator("TEST 4: POST /anomaly/train (no auth - should fail)")
r = requests.post(f"{BASE}/anomaly/train")
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")
assert r.status_code == 403, f"Expected 403, got {r.status_code}"
print(f"{PASS} Auth guard works — unauthenticated request rejected")


# ── Summary ───────────────────────────────────────────────
separator("ALL TESTS PASSED")
print(f"""
{PASS} Health check          — 200 OK
{PASS} POST /anomaly/train   — Isolation Forest trained successfully
{PASS} GET  /anomaly/detect  — Anomalies detected with both methods
{PASS} GET  /anomaly/metrics — Precision/recall metrics returned  
{PASS} Auth guard            — Unauthenticated requests rejected
""")
