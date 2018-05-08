#########
# main_controller
# Nathan Krumholz 
# Diagnostic Biosensors
# 4/29/2018
#########
#Imports - do not remove - 
import numpy as np
import sys
import time
import cv2
import zbar
import RPi.GPIO as GPIO
from PIL import Image
import time
import threading

#########
# SETUP 
#########

i = 0 # first index 
j = 0 # second index 
# these two indexes are used in the logical operation on if a certain 
# function is called or passed. 
terminate = False # = True if the program should end, "kills" all threads

prodlist = [] # list of products that is saved and exported to file 
prodloc = []  # the location of the scanner 

GPIO.setmode(GPIO.BOARD)
DIR_2 = 29   # Direction GPIO Pin
# gpio 5 
PUL_2 = 15   # Step GPIO Pin
# gpio 22 
DIR_3 = 22
# gpio 25
PUL_3 = 18
# gpio 24 
DIR_1 = 37
# gpio 26
PUL_1 = 35
#gpio 19

CW = False    # Clockwise Rotation
SPR = 38    # Steps per set rotation
RET = 0.008  # delay between steps

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
		global i 
		global j
		global terminate
		global RET
		global prodlist
		global prodloc 
		scanner = zbar.ImageScanner()  # initialize scanner
		scanner.parse_config('enable') # allow for the QR code to be a 
										# subsection of the image 
		while not terminate:
			print i 
			if i == j:
				#print "imaging"
				Cam = cv2.VideoCapture(0) 	# turn on camera
				img = Cam.read()[1]


				i += 1
				Cam = None
				#Cam = None # remove to reset buffer 
					#downsample image 
				gray= cv2.resize(img,(600,400), interpolation = cv2.INTER_AREA)
				img = None # remove from memory 
					# convert to grayscale 
				gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY, dstCn=0)
				
					# main diagnostic tool for alignment of camera 
					# images need to be in grayscale 
				#cv2.namedWindow('image', cv2.WINDOW_NORMAL)
				#cv2.imshow('image',gray)
				#cv2.waitKey()
				#cv2.destroyAllWindows()
	
				pil = Image.fromarray(gray)
				gray = None # remove from memory 
				width, height = pil.size
				raw = pil.tobytes()
				pil = None # remove from memory 
					# create a reader
				img = zbar.Image(width, height, 'Y800', raw)
					# scan the image for QRCodes
				scanner.scan(img)
					# extract results and append them to a vector
				for symbol in img:
					prodlist.append(symbol.data)
					prodloc.append(1)
				img = None # remove from memory 
				print prodlist
			else: 
				#print "keep going"
				time.sleep(RET*50)
				

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
		if self.ID < 3:
			# if the ID is 1 then call the mover function 
			self.mtr_mover()
		if self.ID == 3:
			# if the ID is 3 then call the applyr function
			self.mtr_applyr() 
		print("Exiting", self.ID)
	

	def mtr_mover(self):
		# use these global variables 
		global i 
		global j 
		global terminate
		# set the DIR pin to either high or low based on CW variable 
		while not terminate:
			if j<i:
				#print "entering motor controller"
				self.sqr_wave(self.CW)
				if self.ID == 1:
					time.sleep(self.delay*5)
					j += 1 
				#print "end_loop"

				
	def mtr_applyr(self):
		print "entering label applicator" # diagnostic output
		# use these global variables 
		global i 
		global j 
		global terminate
		# set the DIR pin to either high or low based on CW variable 
		
		while not terminate: 
			if j<i:
				self.sqr_wave(self.CW)
				time.sleep(self.delay*3)
				self.sqr_wave(not self.CW)
				self.sqr_wave(not self.CW)
				time.sleep(self.delay*10)

		
	def sqr_wave(self,M):
		# helper function to produce a squre wave that is needed 
		# to drive the stepper motor drivers that we purchased 
		GPIO.output(self.DIR, M)
		#print M
		for x in range(self.count):
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
mtr1 = stprTd(1, DIR_1, PUL_1, RET, SPR, CW)  # label puller 
mtr2 = stprTd(2, DIR_2, PUL_2, RET-.002, SPR+20 , CW)  # sensor puller
mtr3 = stprTd(3, DIR_3, PUL_3, RET-.004, SPR-20, CW)		# label applicator5


###
# start all threads 
# they sould now run simulaneously 
csys1.start()
mtr1.start()
mtr2.start()
mtr3.start()


while not terminate:
	#print i 
	#print j 
	time.sleep(RET*20)
	if i >4:
		terminate = True # terminates all threads safely 
		break # break out of this while loop 
	

#########
#FILING SYSTEM
#########
thefile = open('test.txt', 'w')	# open a file to write to with this name
for item in prodlist:
	thefile.write("%s\n" % item)	# write these values 
thefile.close()
print "end of program"	# diagnostic output 

