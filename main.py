import serial
import time
import uuid
from picamera import PiCamera

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()
    camera = PiCamera()

    while True:

        id = str(uuid.uuid4())
        ser.write(b"THROW\n")

        filename = '/home/pi/Desktop/throws/' + id

        camera.resolution = (480, 480)
        camera.framerate = 90
        camera.color_effects = (128,128)

        camera.start_recording(filename + '.h264', quality=25)
        time.sleep(5)
        camera.stop_recording()
        camera.capture(filename + '.jpg')

        break