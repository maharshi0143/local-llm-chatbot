import requests
import json

try:
    response = requests.post('http://localhost:11434/api/generate',
                           json={
                               'model': 'llama3.2:3b',
                               'prompt': 'Say "Hello, I am working!"',
                               'stream': False
                           })
    if response.status_code == 200:
        result = response.json()
        print("✅ Ollama is running!")
        print(f"🤖 Response: {result.get('response', '')}")
    else:
        print(f"❌ Error: {response.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Make sure Ollama is running (check system tray)")