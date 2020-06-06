import serial
import time
import uuid
import os, sys
import json
import asyncio
from azure.storage.blob.aio import BlobClient
from picamera import PiCamera

def receive_message(msg, ser):
    message_received = False
    while not message_received:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            if(line == msg):
                print("RECEIVED INCOMING MESSAGE: " + line)
                message_received = True

def send_message(msg, ser):
    print("Sending message: " + msg)
    msg = msg + "\n"
    ser.write(msg.encode())

def record_video(camera, filename):
    path = '/home/pi/Desktop/throws/' + filename

    print('Recording Video Start')

    camera.start_recording(path + '.h264', quality=20)
    time.sleep(4)
    camera.stop_recording()

    print('Recording Video End')

    print('Converting Video to .mp4 Start')
    os.system('MP4Box -add ' + path + '.h264:fps=25 ' + path +'.mp4')
    print('Converting Video to .mp4 End')
    
    os.remove(path + '.h264')

def capture_image(camera, filename):
    camera.capture('/home/pi/Desktop/throws/' + filename + '.jpg')

async def upload_file(container, filename, cs):

    print('Uploading Blob Start')
    blob = BlobClient.from_connection_string(
        conn_str=cs, 
        container_name=container, 
        blob_name=os.path.basename(filename))

    with open(filename, "rb") as data:
        await blob.upload_blob(data)
    print('Uploading Blob End')

    os.remove(filename)

async def main():

    with open('config.json') as f:
        d = json.load(f)
        cs = d['BlobConnectionString']

    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()
    camera = PiCamera()
    camera.resolution = (480, 480)
    camera.framerate = 90
    camera.color_effects = (128,128)
    camera.brightness = 60
    camera.contrast = 15

    receive_message("ARDUINO:COMMUNICATION HANDSHAKE", ser)
    send_message("PI:COMMUNICATION HANDSHAKE", ser)

    while True:
        receive_message("ARDUINO:READY TO THROW", ser)

        send_message("PI:THROW", ser)
        
        filename = str(uuid.uuid4())

        record_video(camera, filename)

        send_message("PI:RELOAD", ser)

        await upload_file(
            'autoyahtzee-raw-video-container',
            '/home/pi/Desktop/throws/' + filename + '.mp4', cs)

        send_message("PI:RELOAD", ser)

asyncio.run(main())
