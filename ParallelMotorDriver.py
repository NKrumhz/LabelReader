import threading
import RPi.GPIO as GPIO
import time  

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

CW = True  # Clockwise Rotation
SPR = 200 # Steps per Revolution 
RET = 0.005 # delay between steps 


step_count = SPR
exitFlag = 0

class stprTd(threading.Thread):
	def __init__(self, threadID, DIR, PUL, delay, COUNT, rot):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.DIR = DIR
		self.PUL = PUL
		self.delay = delay
		self.step_count = COUNT
		self.CW = rot
	def run(self):
		print ("Starting ", self.threadID)
		GPIO.setmode(GPIO.BOARD)
		#print self.DIR
		GPIO.setup(self.DIR, GPIO.OUT)
		GPIO.setup(self.PUL, GPIO.OUT)
		#print self.PUL
		self.mtr_ctrl(self.name, self.DIR, self.PUL, self.delay, self.step_count, self.CW)
		
		print ("Exiting ", self.threadID)
		GPIO.cleanup()
		
	def mtr_ctrl(self,threadName, DIR, PUL, delay, count, CW):
		
		GPIO.output(DIR, CW)
		#print self.threadName
		for x in range(count):
			#print "top"
			GPIO.output(PUL, True)
			time.sleep(delay)
			GPIO.output(PUL, False)
			time.sleep(delay)
			#print "bottom"
			
# Create new threads 
#mtr3 = stprTd(1, DIR_3, PUL_3, RET, SPR, CW)
#mtr2 = stprTd(2, DIR_2, PUL_2, RET, SPR , CW)
mtr1 = stprTd(2, DIR_1, PUL_1, RET, SPR , CW)
	# driver for this motor is reversing rotation direction, 
	# so we reverse the direction in the code
#thread2 = stprTd(2, DIR_2, PUL_2, RET, SPR,  CW)
# note: CCW motion unscrews motors 


# start threads
mtr1.start() 
#mtr2.start()
#mtr3.start()


print "exiting main" 


