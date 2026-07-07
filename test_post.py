import urllib.request
import json

data = json.dumps({
    "input": "What government schemes am I eligible for if I am a farmer with annual income below 2 lakhs?",
    "mode": "services",
    "language": "en",
    "temperature": 0.7
}).encode('utf-8')

req = urllib.request.Request('http://localhost:8081/api/generate', data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Error Status:", e.code)
    print("Error Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Other Error:", e)
