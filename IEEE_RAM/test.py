import serial
import time

ser = serial.Serial('/dev/ttyAMA10', 115200, timeout=1)
test_bytes = b'\xAA\xBB\xCC\xDD'

print(f"Sending: {list(test_bytes)}")
ser.write(test_bytes)
time.sleep(0.1)
reply = ser.read(4)
print(f"Received: {list(reply)}")
