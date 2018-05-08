#########
# Alignment controller
# Nathan Krumholz 
# Diagnostic Biosensors
# 4/29/2018
#########
#Imports - do not remove - 
import numpy as np
import sys
import time
import cv2
import RPi.GPIO as GPIO
from PIL import Image
import time
import threading

#########
# SETUP 
#########

terminate = False # = True if the program should end, "kills" all threads

prodlist = [] # list of products that is saved and exported to file 
prodloc = []  # the location of the scanner 

GPIO.setmode(GPIO.BOARD)
DIR_1 = 37
# gpio 26
PUL_1 = 35
#gpio 19


CW = True    # Clockwise Rotation
SPR = 10  # Steps per set rotation
RET = 0.01  # delay between steps

def get_bool(prompt):
    while True:
        try:
           return {"true":True,"false":False}[raw_input(prompt).lower()]
        except KeyError:
           print "Invalid input please enter True or False!"
           
           

class Cam_reader(threading.Thread):
	def _init_(self):
		threading.Thread._Thread__init_(self)

	def run(self):
		print "calling scanner" # diagnostic output
		self.QRScanIO()			# calling QR scanner function 
		print "end of scanning" # diagnostic ouptut
	def QRScanIO(self):
		# use these variabels as their global versions 
		# changes to them here will change them in the global space too

		global RET
		global prodlist
		global prodloc 
				
		while not terminate:
			
			Cam = cv2.VideoCapture(0) 	# turn on camera
			img = Cam.read()[1]			# take picture
			Cam = None
			#Cam = None # remove to reset buffer 
				#downsample image 
			gray= cv2.resize(img,(600,400), interpolation = cv2.INTER_AREA)
			img = None # remove from memory 
				# convert to grayscale 
			gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY, dstCn=0)
			
				# main diagnostic tool for alignment of camera 
				# images need to be in grayscale 
			cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
			cv2.imshow('frame',gray)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
			
		Cam.release()
		cv2.destroyAllWindows()

				

class stprTd(threading.Thread):
	def __init__(self,threadID, DIR, PUL, delay, COUNT, ROT):
		# save these variables to the class to save memory 
		threading.Thread.__init__(self)
		self.ID = threadID
		self.DIR = DIR
		self.PUL = PUL
		self.delay = delay
		self.count = COUNT
		self.CW = ROT
	def run(self):
		print("Motor", self.ID) # diagnostic output
		# setup GPIO pins for output 
		# make sure to only do this once 
		GPIO.setup(self.DIR, GPIO.OUT)
		GPIO.setup(self.PUL, GPIO.OUT)
		# function calls are determined by the thread ID 
		self.mtr_mover()
		print("Exiting", self.ID)
	

	def mtr_mover(self):
		# use these global variables 
		global terminate
		# set the DIR pin to either high or low based on CW variable 
		GPIO.output(self.DIR, self.CW)
		while not terminate:
			terminate = get_bool("Is this position acceptable? [true, false]")
			if terminate == False:
				spr = 0
				spr = input("Enter number of steps to tighten: ")
			print("terminate = ", terminate)
			self.sqr_wave(spr, self.CW)
			#print "end_loop"
		self.mtr_rewind()
				
		
	def sqr_wave(self, numbr, CW):
		# helper function to produce a squre wave that is needed 
		# to drive the stepper motor drivers that we purchased 
		GPIO.output(self.DIR, CW)
		for x in range(numbr):
			#print(x)  					# diagnostic output 
			GPIO.output(self.PUL,True)  # produce high signal
			time.sleep(self.delay)		# hold signal high
			GPIO.output(self.PUL,False) # produce low signal
			time.sleep(self.delay) 		# hold signal low 
			#print "bottom"				# diagnostic output

#########
#MAIN
#########

csys1 = Cam_reader()
mtr1 = stprTd(1, DIR_1, PUL_1, RET, SPR, CW)

###
# start all threads 
# they sould now run simulaneously 
csys1.start()
mtr1.start()



while not terminate:
	#print i 
	#print j 
	time.sleep(RET*100)


