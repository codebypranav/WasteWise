import serial
import requests
import json
import time

def forward_to_backend(data):
    try:
        print(f"Attempting to send data to backend: {data}")
        response = requests.post('http://35.21.212.228:5000/api/current-stats', json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending to backend: {e}")
        return False

def main():
    PORT = '/dev/cu.usbserial-141230'
    BAUD_RATE = 115200

    while True:
        try:
            print(f"Attempting to connect to {PORT}...")
            ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
            print("Serial connection established")
            
            buffer = ""
            while True:
                if ser.in_waiting:
                    char = ser.read().decode('utf-8')
                    if char == '\n':
                        line = buffer.strip()
                        print(f"Raw data received: '{line}'")
                        
                        # Extract fill level from log message
                        if "Fill Level:" in line:
                            try:
                                fill_level = float(line.split("Fill Level: ")[1].replace("%", ""))
                                data = {"fill_level": fill_level}
                                print(f"Extracted data: {data}")
                                success = forward_to_backend(data)
                                if not success:
                                    print("Failed to send data to backend")
                            except Exception as e:
                                print(f"Error extracting fill level: {e}")
                        
                        buffer = ""
                    else:
                        buffer += char
                        
                time.sleep(0.1)
                
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()