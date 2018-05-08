import numpy as np
import sys
import time
import cv2
import zbar
from PIL import Image

# will return index 
def indices(a,func) :
	return [i for (i, val) in enumerate(a) if func(val)]

def pollItem() :
	prodcall = raw_input("Enter item you wish to call: ")
	idx = indices(prodlist, lambda x: x == prodcall)
	print idx
	
	# initializing arrays 
prodlist= []
prodloc = []

	# initialize a scanner
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

fls = ['RW_QRcode1.png','RW_QRcode1.png', 'test_QR.png', 'RW_QRcode1.png','test_QR.png'] 

print 'start'
i = 0
# raw detection code
while i<1:
	Cam = cv2.VideoCapture(1) 	# turn on camera
	img = Cam.read()[1]

	i += 1
	Cam = None
	#img = cv2.imread(fls[i],0)
		#downsample image 
	gray= cv2.resize(img,(600,400), interpolation = cv2.INTER_AREA)
	img = None # remove from memory 
		# convert to grayscale 
	gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY, dstCn=0)
	
	cv2.namedWindow('image', cv2.WINDOW_NORMAL)
	cv2.imshow('image',gray)
	cv2.waitKey()
	cv2.destroyAllWindows()
	
	pil = Image.fromarray(gray)
	width, height = pil.size
		# output image size in pixles 
	#print width, height 
	raw = pil.tobytes()
	pil = None 
		# create a reader
	img = zbar.Image(width, height, 'Y800', raw)
		# scan the image for QRCodes
	scanner.scan(img)
		# extract results and append them to a vector
	for symbol in img:
		prodlist.append(symbol.data)
		prodloc.append(1)
		#print prodlist
	i += 1
	img = None
	#print prodlist

	# testing recall functionality 
print prodlist
#pollItem()
