import requests
import time

def send_test_data():
    url = 'http://localhost:5000/api/current-stats'
    headers = {'Content-Type': 'application/json'}

    test_data = {
        "recyclable": 30.0,      
        "organic": 44.0,        
        "non_recyclable": 26.0, 
        "temperature": 72     
    }

    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_test_data() 