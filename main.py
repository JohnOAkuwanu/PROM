from datetime import datetime        
import tkinter
import argparse
import os
import numpy
from constants import *
#import smbus
from PIL import Image, ImageDraw

IMAGE_DETECTIONS = 0
MICROPHONE_DETECTIONS = 0
TOTAL_DETECTIONS = IMAGE_DETECTIONS + MICROPHONE_DETECTIONS

def captureImage():
    while True:
        #LEDControl(1)
        os.system("fswebcam -r " + RESOLUTION + " -S 4 --no-banner image.jpg") #capture
        #LEDControl(0)
        imageDetection("image.jpg")
        os.remove("image.jpg") #cleanup
        
def captureMicrophone():
    #LEDControl(1)
    microphoneDetection() #change GUI state
    #LEDControl(0)
    
def imageDetection(file):

    image = Image.open(file)
    pixels = numpy.array(image).reshape(-1, 3)
        
    for i in range(0, len(pixels) - 1):
        if pixels[i, 0] < 140 and pixels[i, 1] > pixels[i, 0] and pixels[i, 1] > pixels[i, 2]: #g > r, g > b, r < 150 #10, 40, 50
            dt = datetime.now()
            log("Image", dt)
            draw(file, dt)
            global IMAGE_DETECTIONS
            IMAGE_DETECTIONS += 1
            break
        i += 1
    
def draw(file, now):
    image = Image.open(file)
    width, height = image.size
    dimX = []
    dimY = []
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = image.getpixel((x, y))
            if r  < 140 and g > r and g > b:#if(r < 20 and g < 40 and b < 50):
                dimX.append(x)
                dimY.append(y)
            y += 1
        x += 1
    ImageDraw.Draw(image).rectangle([min(dimX), min(dimY), max(dimX), max(dimY)], outline="red")
    image.save(now.strftime("%H-%M-%S_%d.%m.%Y") + ".ppm")

def microphoneDetection():
    bus = smbus.SMBus(1)
    while True:
        bus.write_byte(I2CADDRESS, 0x20)
        temp = bus.read_word_data(I2CADDRESS, 0x00)
        firstHalf = temp >> 8
        secondHalf = temp << 8
        switched = firstHalf | secondHalf
        comparisonValue = switched & 0x0FFF

        if comparisonValue > THRESHOLD:
            log("Microphone", datetime.now())
            global MICROPHONE_DETECTIONS
            MICROPHONE_DETECTIONS += 1
            break

def LEDControl(control):
    if control == 0:
        #OFF
        #Red LED
        return
    elif control == 1:
        #ON
        #Yellow LED
        return
    else:
        raise Exception("Out of range.")

def GUI():
    root = tkinter.Tk(className="Cockroach ID")
    cameraStatus = tkinter.Label(root, text="Camera: ").pack()
    cameraDetections = tkinter.Label(root, text="Camera Detections: ").pack()
    microphoneStatus = tkinter.Label(root, text="Microphone: ").pack()
    microphoneDetections = tkinter.Label(root, text="Microphone Detections: ").pack()
    systemState = tkinter.Label(root, text="System State: ").pack()
    PWM = tkinter.Button(root, text="Toggle PWM").pack()
    servo = tkinter.Button(root, text="Toggle Servo Motor Supply").pack()
    root.mainloop()

#def togglePWM():
#def toggleServo():
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(10,GPIO.OUT)

p = GPIO.PWM(10,50)
p.start(7.5)

try:
        while True:
                p.ChangeDutyCycle(7.5)
                time.sleep(1)
                p.ChangeDutyCycle(12.5)
                time.sleep(1)
                p.ChangeDutyCycle(2.5)
                time.sleep(1)


except KeyboardInterrupt:
        GPIO.cleanup
#
    
def log(type, now):
    print(type + ": Bug detected - " + now.strftime("%H:%M:%S %d/%m/%y"))
    with open("log.csv", "a") as log:
        log.write(type + "," + now.strftime("%d/%m/%y") + "," + now.strftime("%H:%M:%S\n"))
    
#def imageProcessing():

detector = argparse.ArgumentParser(description="Cockroach detection")
detector.add_argument() #one image
detector.add_argument() #repeatedly take images
detector.add_argument() #microphone
detector.add_argument() #gui

imageDetection("./images/image3.jpg")

# 
I2C_YEL_LED = 0x38
LED_ON = 0x00
LED_OFF =0xFF

bus = smbus.SMBus(1)

bus.write_byte( I2C_YEL_LED, LED_ON )
time.sleep(1)
bus.write_byte( I2C_YEL_LED, LED_OFF )
time.sleep(1)
#
