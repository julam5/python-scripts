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
txtName = "AirdroneImgSet.txt"
sourceAddr = "/home/justin/server-dataset"
dstDir = "./redoneLabels"
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

    for root, dirs, files in os.walk(clipDirName, topdown=False):
        for name in files:
            if (name.rfind(tag1) != -1 ):
                nameList.append(os.path.join(os.path.basename(root), name))          

    return naturalsort(nameList)

def saveNatSort(clipNames):
    savingFile = open(txtName, "wb")
    for name in clipNames:
        savingFile.write("%s\n" % name)
    savingFile.close()


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

	def adjustWidthNmidX(self,below0,imgWidth):
		if (below0):
			self.topLeftX = 0
		else:
			self.botRightX = imgWidth

		self.widthDeNorm = self.botRightX - self.topLeftX
		self.midXDeNorm = self.topLeftX + (self.widthDeNorm/2)

	def adjustHeightNmidY(self,below0,imgHeight):
		if (below0):
			self.topLeftY = 0
		else:
			self.botRightY = imgHeight

		self.heightDeNorm = self.botRightY - self.topLeftY
		self.midYDeNorm = self.topLeftY + (self.heightDeNorm/2)


# ============================================================================== SrcImage object
class SrcImage():
	global sourceAddr, cropDim
# ------------------------------------------------------------------------- creates the Img object
	def __init__(self, srcLabel):   
		self.baseLabel = os.path.basename(srcLabel)
		self.baseClip = self.baseLabel.rstrip('.txt') + ".png"

		self.srcLabel = sourceAddr + "/labels/" + srcLabel
		self.srcClip = sourceAddr + "/images/" + srcLabel.rstrip('.txt') + ".png"

		if (os.path.isdir(dstDir + "/" +os.path.dirname(srcLabel)) is False): 
			print "> " + dstDir + "/" + os.path.dirname(srcLabel) + " is not a valid path! Creating it now."
			os.makedirs(dstDir + "/" + os.path.dirname(srcLabel))

		self.dstLabel = dstDir + "/" + srcLabel

		self.clusterNum = -1

		self.imgWidth = 0
		self.imgHeight = 0
		self.imgWindow = cv2.imread(self.srcClip)
		self.cropWindow = None
		self.currentCroppedClip = None

		self.rectsFetched = [] # holds bboxes from label txt (Rectangles)

# ------------------------------------------------------------------------- print image info
	def __str__(self):
		return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
		"Src Clip path: " + self.srcClip + "\n" + \
		"Src Label path: " + self.srcLabel + "\n" + \
		"Dst Label path: " + self.dstLabel + "\n" + \
		"Cluster number: " + str(self.clusterNum) + "\n" +	\
		"ImgWidth: " + str(self.imgWidth) + "\n" + \
		"ImgHeight: " + str(self.imgHeight) + "\n" \
		+ "+++++++++++++++++++++++++\n"

	def setOrigImgDim(self):
		self.imgWidth = self.imgWindow.shape[1]
		self.imgHeight = self.imgWindow.shape[0]

	def readContent(self):                                                      
		txtFile = open(self.srcLabel,"r")
		for content in iter(txtFile):
			contentN = content.rstrip('\n')
			#parsed format = "class id", "center point x coord", " center point y coord", "width", "height" 
			parsed = contentN.split()
			self.clusterNum = int(parsed[0])
			rectangle = Rectangle(parsed[1], parsed[2], parsed[3], parsed[4], True)

			self.rectsFetched.append(rectangle)
			#break # only do the first bounding box

		txtFile.close()


	def denormalizeRectsFetched(self):
		for rectangle in self.rectsFetched:
			rectangle.denormalize(self.imgHeight, self.imgWidth)
			#print rectangle

	def bboxesNeededAdjust(self):
		status = False
		for rectangle in self.rectsFetched:
			if (rectangle.topLeftX < 0):
				rectangle.adjustWidthNmidX(True,self.imgWidth)
				status = True

			if (rectangle.topLeftY < 0):
				rectangle.adjustHeightNmidY(True,self.imgHeight)
				status = True	

			if (rectangle.botRightX > self.imgWidth):
				rectangle.adjustWidthNmidX(False,self.imgWidth)
				status = True				

			if (rectangle.botRightY > self.imgHeight):
				rectangle.adjustHeightNmidY(False,self.imgHeight)
				status = True				
		return status		

	def normalizeNewBbox(self):
		for rectangle in self.rectsFetched:
			rectangle.normalize(self.imgHeight, self.imgWidth)
			#print rectangle

	def saveNewLabel(self):
		savingFile = open(self.dstLabel, "wb")
		for rectangle in self.rectsFetched:
			item = str(self.clusterNum) + " " + str(rectangle.midXNorm) + " " + str(rectangle.midYNorm) + " " + str(rectangle.widthNorm) + " " + str(rectangle.heightNorm)
			savingFile.write("%s\n" % item)
		savingFile.close()

# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- take in arguments
parser = argparse.ArgumentParser(description='ReCalculate Labels')

parser.add_argument('-s', type=str, default=''  , dest='labelSource' , help='source dir of label files')

parsedArgs = parser.parse_args()

if (len(parsedArgs.labelSource) != 0 and parsedArgs.labelSource[len(parsedArgs.labelSource)-1] == '/'):
    labelSource = parsedArgs.labelSource[0:-1]
else:
    labelSource = parsedArgs.labelSource


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if (os.path.isdir(labelSource) is False): 
    print "> " + labelSource + " is not a valid path!"
    raise SystemExit

clipNames = generate_clipfile(labelSource) # format of each line => clip#/clip#-sub#.txt

#saveNatSort(clipNames)

if (os.path.isdir(dstDir) is False): 
	print "> " + dstDir + " is not a valid path! Creating it now."
	os.makedirs(dstDir)

for clip in clipNames:
	currentClip = SrcImage(clip) 
	currentClip.setOrigImgDim()	
	currentClip.readContent()
	currentClip.denormalizeRectsFetched()
	if (currentClip.bboxesNeededAdjust()):
		currentClip.normalizeNewBbox()
		currentClip.saveNewLabel()
		#print currentClip
		#break