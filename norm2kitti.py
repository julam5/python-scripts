#!/usr/bin/env python

import os
import argparse
import csv
import numpy as np
import cv2

#-------------------------------------------------------------- from rosettacode
from itertools import groupby
from unicodedata import decomposition, name
from pprint import pprint as pp
#####################################################################################################################   GLOBAL VARIABLES
txtName = "norm2kitti.txt"
sourceAddr = "."
dstDir = "./norm2kitti"
countup = 0
#####################################################################################################################   GLOBAL FUNCTIONS
# =============================================================================================================== Natural sorting 
#-------------------------------------------------------------- from rosettacode
commonleaders = ['the'] # lowercase leading words to ignore
 
hexdigits = set('0123456789abcdef')
decdigits = set('0123456789')   # Don't use str.isnumeric
 
def splitchar(c):
    ' De-ligature. De-accent a char'
    de = decomposition(c)
    if de:
        de = [d for d in de.split()
                  if all(c.lower()
                         in hexdigits for c in d)]
        n = name(c, c).upper()
        if 'LIGATURE' in n:
            base += others.pop(0)
    else:
        base = c
    return base
 
 
def sortkeygen(s):
    s = unicode(s).strip()
    s = ' '.join(s.split())
    s = s.lower()
    words = s.split()
    if len(words) > 1 and words[0] in commonleaders:
        s = ' '.join( words[1:])
    s = ''.join(splitchar(c) for c in s)
    s = [ int("".join(g)) if isinteger else "".join(g)
          for isinteger,g in groupby(s, lambda x: x in decdigits)]
 
    return s
 
def naturalsort(items):
    return sorted(items, key=sortkeygen)
# =============================================================================================================== Natural sorting 
# =============================================================================================================== Generate clipFile.txt
def generate_clipfile(clipDirName):
    print "> Generating label list"

    tag1=".txt" #
    nameList = []

    for root, dirs, files in os.walk(clipDirName):
        for name in files:
            if (name.rfind(tag1) != -1 ):
                nameList.append(os.path.join(os.path.basename(root), name))          

    return naturalsort(nameList)

def saveNatSort(clipNames):
    savingFile = open(txtName, "wb")
    for name in clipNames:
        savingFile.write("%s\n" % name)
    savingFile.close()

def readArguments():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-s', type=str, default=None, dest='srcTop', help='source label dir path')

    parsedArgs = parser.parse_args()

    if (parsedArgs.srcTop == None):    
        print "> No labels directory path entered!"
        raise SystemExit

    if (parsedArgs.srcTop[-1] == '/'):
        srcTop = parsedArgs.srcTop[0:-1]
    else:
        srcTop = parsedArgs.srcTop

    srcTop = os.path.expanduser(srcTop)
    print "> Verifying source clip directory"
    ifNotDirExit(srcTop)

    return srcTop
# ---------------------------------------------------------------- check if path is directory, if not exit program
def ifNotDirExit(directoryName):
    if (os.path.isdir(directoryName) is False): 
        print "> " + directoryName + " is not a valid directory! Exiting."
        raise SystemExit
    else:
        print "> Found directory: " + directoryName 
# ---------------------------------------------------------------- check if path is directory, if not exit program
def ifNotDirCreate(directoryName):
    if (os.path.isdir(directoryName) is False): 
        print "> " + directoryName + " is not a valid directory! Creating it."
        os.makedirs(directoryName)
    #else:
        #print "> Found directory: " + directoryName 
# #######################################################################################   Classes
# ============================================================================== Rectangle object
class Rectangle():
	def __init__(self, midX=0, midY=0, width=0, height=0, initiallyNorm=True):      

		# normalized points for txt file
		if (initiallyNorm):
			self.midXNorm = float(midX)
			self.midYNorm = float(midY)
			self.widthNorm = float(width)
			self.heightNorm = float(height)

			self.midXDeNorm = 0
			self.midYDeNorm = 0
			self.widthDeNorm = 0
			self.heightDeNorm = 0

			self.topLeftX = 0
			self.topLeftY = 0
			self.botRightX = 0
			self.botRightY = 0

			self.areaDeNorm = 0

		else:
			self.midXNorm = 0
			self.midYNorm = 0
			self.widthNorm = 0
			self.heightNorm = 0

			self.midXDeNorm = int(midX)
			self.midYDeNorm = int(midY)
			self.widthDeNorm = int(width)
			self.heightDeNorm = int(height)

			self.topLeftX = self.midXDeNorm - (self.widthDeNorm/2)
			self.topLeftY = self.midYDeNorm - (self.heightDeNorm/2)
			self.botRightX = self.midXDeNorm + (self.widthDeNorm/2)
			self.botRightY = self.midYDeNorm + (self.heightDeNorm/2)

			self.areaDeNorm = self.widthDeNorm * self.heightDeNorm

	# ------------------------------------------------------------------------- print rectangle info
	def __str__(self):
		return "============================== Rectangle\n" \
			"MidXNorm: "    + str(self.midXNorm) + "\n" \
			"MidYNorm: "    + str(self.midYNorm) + "\n" \
			"WidthNorm: "   + str(self.widthNorm) + "\n" \
			"HeightNorm: "  + str(self.heightNorm) + "\n" \
			"----------------------------\n" \
			"MidXDeNorm: "      + str(self.midXDeNorm) + "\n" \
			"MidYDeNorm: "      + str(self.midYDeNorm) + "\n" \
			"WidthDeNorm: "     + str(self.widthDeNorm) + "\n" \
			"HeightDeNorm: "    + str(self.heightDeNorm) + "\n" \
			"AreaDeNorm: "      + str(self.areaDeNorm) + "\n" \
			"----------------------------\n" \
			"topLeftX: "      + str(self.topLeftX) + "\n" \
			"topLeftY: "     + str(self.topLeftY) + "\n" \
			"botRightX: "    + str(self.botRightX) + "\n" \
			"botRightY: "      + str(self.botRightY) + "\n" \
			"==============================\n" \
	# ------------------------------------------------------------------------- normalize points of rectangle
	def normalize(self, imgRows, imgColmns):  
		self.midXNorm   = "%.6f" %  ((self.midXDeNorm) / float(imgColmns))
		self.midYNorm   = "%.6f" %  ((self.midYDeNorm) / float(imgRows))
		self.widthNorm  = "%.6f" %  ((self.widthDeNorm) / float(imgColmns))
		self.heightNorm = "%.6f" %  ((self.heightDeNorm) / float(imgRows))

	def denormalize(self, imgRows, imgColmns):
		floatImgRows = imgRows
		floatImgColmns = imgColmns

		self.midXDeNorm 	= int(round(self.midXNorm * imgColmns))
		self.midYDeNorm 	= int(round(self.midYNorm * imgRows))
		self.widthDeNorm 	= int(round(self.widthNorm * imgColmns))
		self.heightDeNorm 	= int(round(self.heightNorm * imgRows))

		self.topLeftX = self.midXDeNorm - (self.widthDeNorm/2)
		self.topLeftY = self.midYDeNorm - (self.heightDeNorm/2)
		self.botRightX = self.midXDeNorm + (self.widthDeNorm/2)
		self.botRightY = self.midYDeNorm + (self.heightDeNorm/2)

		self.areaDeNorm = self.widthDeNorm * self.heightDeNorm

# ============================================================================== SrcImage object
class SrcLabel():
	global sourceAddr, cropDim
# ------------------------------------------------------------------------- creates the Img object
	def __init__(self, srcLabel):   
		self.baseLabel = os.path.basename(srcLabel)
		self.srcLabel = sourceAddr + "/labels/" + srcLabel

		self.baseClip = self.baseLabel.rstrip('.txt') + ".png"
		self.srcClip = sourceAddr + "/images/" + srcLabel.rstrip('.txt') + ".png"

		if (os.path.isdir(dstDir + "/" +os.path.dirname(srcLabel)) is False): 
			print "> " + dstDir + "/" + os.path.dirname(srcLabel) + " is not a valid path! Creating it now."
			os.makedirs(dstDir + "/" + os.path.dirname(srcLabel))

		self.clusterNum = -1
		self.dstLabel = dstDir + "/" + srcLabel

		self.imgWidth = 0
		self.imgHeight = 0
		self.imgWindow = cv2.imread(self.srcClip)
		self.cropWindow = None
		self.resizeWindow = None
		self.currentCroppedClip = None

		self.rectsFetched = [] # holds bboxes from label txt (Rectangles)

# ------------------------------------------------------------------------- print image info
	def __str__(self):
		return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
		"Src Img path: " + self.srcLabel + "\n" + \
		"Src Label path: " + self.srcLabel + "\n" + \
		"Dst Label path: " + self.dstLabel + "\n" + \
		"Cluster number: " + str(self.clusterNum) + "\n" +	\
		"ImgWidth: " + str(self.imgWidth) + "\n" + \
		"ImgHeight: " + str(self.imgHeight) + "\n" \
		+ "+++++++++++++++++++++++++\n"

	def readContent(self):                                                      
		txtFile = open(self.srcLabel,"r")
		for content in iter(txtFile):
			contentN = content.rstrip('\n')
			#parsed format = "class id", "center point x coord", " center point y coord", "width", "height" 
			parsed = contentN.split()
			self.clusterNum = int(parsed[0])
			rectangle = Rectangle(parsed[1], parsed[2], parsed[3], parsed[4])

			self.rectsFetched.append(rectangle)
			#print rectangle
			#break # only do the first bounding box

		txtFile.close()

	def setOrigImgDim(self):
		self.imgWidth = self.imgWindow.shape[1]
		self.imgHeight = self.imgWindow.shape[0]

	def denormalizeRectsFetched(self):
		for rectangle in self.rectsFetched:
			rectangle.denormalize(self.imgHeight, self.imgWidth)
			#print rectangle

	def saveNewLabel(self):
		savingFile = open(self.dstLabel, "wb")
		for rectangle in self.rectsFetched:
			# type, truncated, occluded, alpha, (4) bbox, (3) dimensions, (3) location, rotation_y, score
			item = ("Drone -1 -1 -10 " + '{}.00' + " " + '{}.00' + " " + '{}.00' + " " + '{}.00' + " " + "-1 -1 -1 -1000 -1000 -1000 -10") \
			.format(rectangle.topLeftX,rectangle.topLeftY,rectangle.botRightX,rectangle.botRightY)
			savingFile.write("%s\n" % item)
		savingFile.close()

# #######################################################################################   MAIN CODE START

topDirPath = readArguments()

clipNames = generate_clipfile(topDirPath) # format of each line => clip#/clip#-sub#.txt

#saveNatSort(clipNames)

ifNotDirCreate(dstDir)

for clip in clipNames:
	currentClip = SrcLabel(clip) 
	currentClip.readContent()

	if (len(currentClip.rectsFetched) > 0):
		currentClip.setOrigImgDim()
		#print currentClip
		currentClip.denormalizeRectsFetched()
		currentClip.saveNewLabel()

#print len(clipNames)
