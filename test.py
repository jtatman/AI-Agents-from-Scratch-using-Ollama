import requests

server_address = "http://localhost:11434"  # Replace with your server address
model_name = "llama3.2:3b"  # Replace with your desired model

payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": "Hello, how are you?"}
    ]
}

response = requests.post(f"{server_address}/api/chat", json=payload)
response.raise_for_status()
print("Response:", response.json()["message"]["content"])