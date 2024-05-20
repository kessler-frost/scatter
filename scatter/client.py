import requests


response = requests.get(
    "http://127.0.0.1:8000/add", json={
        "a": 1,
        "b": 2
    }
)

print(response.json())
