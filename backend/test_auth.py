import urllib.request, json, urllib.error
req = urllib.request.Request('http://127.0.0.1:8000/auth/register', method='POST', headers={'Content-Type': 'application/json'}, data=json.dumps({'name': 'Test User', 'email': 'test@gmail.com', 'password': 'password123'}).encode('utf-8'))
try:
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode('utf-8'))
