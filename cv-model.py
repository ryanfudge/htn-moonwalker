import base64
import requests
import json
import cv2

import time
import serial
import pyvesc
import RPi.GPIO as GPIO

DIV_CONST = 15
SLEEP_TIME = 0.0001

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)
right_brake = GPIO.PWM(11,50)
left_brake = GPIO.PWM(12,50)
throttle = GPIO.PWM(29,50)
right_brake.start(0)
left_brake.start(0)
throttle.start(0)

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

def changeDuty(num):
    ser.write(pyvesc.encode(pyvesc.SetDutyCycle(num)))
    time.sleep(SLEEP_TIME)

def main():
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    url = 'http://10.37.103.68:4000/yolo_endpoint/'
    headers = {
        "Content-Type": "application/json"
    }

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            # Resize the frame to reduce data size
            frame_resized = cv2.resize(frame, (640, 480)) 

            # Encode the frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame_resized)
            if not ret:
                print("Failed to encode frame")
                continue

            # Convert to Base64
            encoded_image = base64.b64encode(buffer).decode('utf-8')

            payload = {
                "image": encoded_image,
                "filename": "captured_frame.jpg"
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                if response.status_code == 200:
                    print(str(response.json()))

                    if (str(response.json()) == "{'message': 'No detections found!'}"):
                        throttle.ChangeDutyCycle(2 + (5 / 18))
                        angle = 90
                        right_brake.ChangeDutyCycle(2 + (angle / 18))
                        left_brake.ChangeDutyCycle(2 + (angle / 18))
                    elif (str(response.json()) == "{'direction': 'center'}"):
                        throttle.ChangeDutyCycle(2 + (10 / 18))
                        angle = 90
                        right_brake.ChangeDutyCycle(2 + (angle / 18))
                        left_brake.ChangeDutyCycle(2 + (angle / 18))
                    elif (str(response.json()) == "{'direction': 'right'}"):
                        angle = 0
                        right_brake.ChangeDutyCycle(2 + (angle / 18))
                    elif (str(response.json()) == "{'direction': 'left'}"):
                        angle = 180
                        left_brake.ChangeDutyCycle(2 + (angle / 18))
                else:
                    print(f"Failed to upload image. Status code: {response.status_code}, Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")

    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
