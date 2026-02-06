import requests
import json

# Client script to interact with server
SERVER_URL = "http://127.0.0.1:5000"

def login(username, password):
    payload = {
        "student": username,
        "password": password
    }

    response = requests.post(f"{SERVER_URL}/login", json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json}")
    return response


if __name__ == "__main__":
    login("student", "secret")