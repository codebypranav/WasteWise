import requests
import time

def send_test_alert():
    url = 'http://localhost:5000/api/alerts'
    headers = {'Content-Type': 'application/json'}

    # Example alert data
    test_alert = {
        "message": "High temperature detected in bin",
        "location": "Building C, Floor 1",
        "is_read": False
    }

    try:
        response = requests.post(url, json=test_alert, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_test_alert() 