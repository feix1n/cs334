import serial
import time
import threading

from gpiozero import Button

switchp1a = Button(14)
switchp2a = Button(15)
switchp1b = Button(23)
switchp2a = Button(24)

class ESP32Data:
    def __init__(self):
        self.momentary = False
        self.joystick_sw = False
        self.coordinates = []
        self.buttonHeldTime = 0
        self.is_ready = False  # Flag to track if the "Player is ready" message has been printed

    def __str__(self):
        return f"Momentary: {self.momentary}, JoystickSW: {self.joystick_sw}, Coordinates: {self.coordinates}"

    def update_momentary(self, value):
        self.momentary = value

    def update_joystick_sw(self, value):
        self.joystick_sw = value

    def update_coordinates(self, x, y):
        self.coordinates = [(x, y)]

def ready_state(esp32_data):
    if esp32_data.momentary:
        curr_time = time.time()
        
        if esp32_data.buttonHeldTime == 0:
            esp32_data.buttonHeldTime = curr_time
            print("Countdown started")
        elif curr_time - esp32_data.buttonHeldTime >= 5:
            if not esp32_data.is_ready: 
                print("Player is ready")
                esp32_data.is_ready = True  
    else:
        esp32_data.buttonHeldTime = 0
        esp32_data.is_ready = False  

def read_serial_data(serial_port, esp32_data):
    try:
        with serial.Serial(serial_port, 115200) as ser:
            print(f"Reading from {serial_port}...")
            while True:
                if ser.in_waiting > 0: 
                    line = ser.readline().decode('utf-8').strip() 
                    if "Momentary" in line:
                        if "On" in line:
                            esp32_data.update_momentary(True)
                        elif "Off" in line:
                            esp32_data.update_momentary(False)
                    elif "JoystickSW" in line:
                        if "On" in line:
                            esp32_data.update_joystick_sw(True)
                        elif "Off" in line:
                            esp32_data.update_joystick_sw(False)
                    elif "x =" in line and "y =" in line:
                        parts = line.split(',')
                        x_value = int(parts[0].split('=')[1].strip())
                        y_value = int(parts[1].split('=')[1].strip())
                        esp32_data.update_coordinates(x_value, y_value)

                    print(f"Data from {serial_port}: {esp32_data}")
                time.sleep(0.1)  # Prevent busy-waiting (avoid high CPU usage)
    except Exception as e:
        print(f"Error reading serial data: {e}")

def main():
    serial_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']
    player1 = ESP32Data()

    # Start a thread to read serial data
    serial_thread = threading.Thread(target=read_serial_data, args=(serial_ports[0], player1), daemon=True)
    serial_thread.start()

    try:
        while True:
            ready_state(player1) 
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("Program interrupted, exiting...")
