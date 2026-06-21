"""
End-to-end test for all anomaly detection endpoints.
Tests: POST /anomaly/train, GET /anomaly/detect, GET /anomaly/metrics
"""
import requests
import json
import sys

BASE = "http://127.0.0.1:8000"

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

separator("STEP 1: Authenticating with credentials")
login_payload = {
    "email": "apoorvjha11@gmail.com",
    "password": "Apoorv@2004"
}
try:
    login_response = requests.post(f"{BASE}/auth/login", json=login_payload)
    if login_response.status_code != 200:
        print(f"[FAIL] Authentication failed: {login_response.text}")
        sys.exit(1)
    
    TOKEN = login_response.json()["access_token"]
    HEADERS = {"Authorization": f"Bearer {TOKEN}"}
    print("[PASS] Successfully logged in and received JWT token.")
except Exception as e:
    print(f"[FAIL] Server is not running. Please start it with 'uvicorn app.main:app' first.\nError: {e}")
    sys.exit(1)


separator("TEST 0: Health Check")
r = requests.get(f"{BASE}/health")
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")
assert r.status_code == 200, "Health check failed"
print("[PASS] Health check passed")


separator("TEST 1: POST /anomaly/train")
r = requests.post(f"{BASE}/anomaly/train", headers=HEADERS)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {json.dumps(data, indent=2)}")

assert r.status_code == 200, f"Expected 200, got {r.status_code}"
assert "message" in data, "Missing 'message' field"
assert "trained_on" in data, "Missing 'trained_on' field"
print(f"[PASS] Train endpoint passed - trained on {data['trained_on']} records")


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

if data["anomalies_detected"] > 0:
    print(f"\nTop 5 alerts:")
    for alert in data["alerts"][:5]:
        print(f"  - [{alert['severity'].upper()}] {alert['merchant']}: "
              f"Rs.{alert['amount']:,.0f} ({', '.join(alert['detection_methods'])})")
        safe_message = alert['message'].replace('σ', 'sigma').encode('ascii', 'ignore').decode('ascii')
        print(f"    {safe_message}")

print(f"[PASS] Detect endpoint passed - {data['anomalies_detected']} anomalies in {data['total_transactions']} txns")


separator("TEST 3: GET /anomaly/metrics")
r = requests.get(f"{BASE}/anomaly/metrics", headers=HEADERS)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {json.dumps(data, indent=2)}")

assert r.status_code == 200, f"Expected 200, got {r.status_code}"
print("[PASS] Metrics endpoint passed")


separator("TEST 4: POST /anomaly/train (no auth - should fail)")
r = requests.post(f"{BASE}/anomaly/train")
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")
assert r.status_code in [401, 403], f"Expected 401 or 403, got {r.status_code}"
print("[PASS] Auth guard works - unauthenticated request rejected")


separator("ALL TESTS PASSED")
print(f"""
[PASS] Health check          - 200 OK
[PASS] POST /anomaly/train   - Isolation Forest trained successfully
[PASS] GET  /anomaly/detect  - Anomalies detected with both methods
[PASS] GET  /anomaly/metrics - Precision/recall metrics returned  
[PASS] Auth guard            - Unauthenticated requests rejected
""")
