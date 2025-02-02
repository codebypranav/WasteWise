import serial
import requests
import json
import time

def forward_to_backend(data):
    try:
        response = requests.post('http://35.21.212.228:5000/api/current-stats', json=data)  # Update IP here
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
    except Exception as e:
        print(f"Error sending to backend: {e}")

def main():
    PORT = '/dev/cu.usbserial-141230'
    BAUD_RATE = 115200

    while True:
        try:
            print(f"Attempting to connect to {PORT}...")
            ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
            print("Serial connection established")
            
            while True:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    if line.startswith('DATA:'):  # Only process lines with our prefix
                        json_str = line[5:]  # Remove the 'DATA:' prefix
                        try:
                            data = json.loads(json_str)
                            forward_to_backend(data)
                        except json.JSONDecodeError as e:
                            print(f"JSON parsing error: {e}")
                            print(f"Problematic JSON: '{json_str}'")
                time.sleep(0.1)
                
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()