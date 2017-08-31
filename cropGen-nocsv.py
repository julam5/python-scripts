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
topDirName = "./airdroneroi"
cropDim = 720 #448
resizeDim = 448
countup = 0
minBboxArea = 32 * 32
currClusterNum = 0

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

# ============================================================================== CropImage object
class CropImage():
	def __init__(self,startXcrop,startYcrop):
		self.newOriginX = startXcrop
		self.newOriginY = startYcrop


# ============================================================================== SrcImage object
class SrcImage():
	global cropDim, minBboxArea, resizeDim
# ------------------------------------------------------------------------- creates the Img object
	def __init__(self, srcClip, clusterNum):   
		self.baseClipName = os.path.basename(srcClip).rstrip('.png')
		self.srcClip = srcClip
		self.srcLabel = (srcClip.replace("images","labels")).rstrip('.png') + ".txt"
		self.dstClip = None
		self.dstLabel = None

		self.clusterNum = clusterNum

		self.imgWidth = 0
		self.imgHeight = 0
		self.imgWindow = cv2.imread(self.srcClip)
		self.cropWindow = None
		self.resizeWindow = None
		self.currentCroppedClip = None

		self.rectsFetched = [] # holds bboxes from label txt (Rectangles)
		self.bboxesWithin = [] # holds bboxes found in current cropped clip (ints)
		self.rectsCropped = [] # holds bboxes readjusted from cropped clip (Rectangles)

# ------------------------------------------------------------------------- print image info
	def __str__(self):
		return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
		"SrcClip path: " + self.srcClip + "\n" + \
		"SrcLabel path: " + self.srcLabel + "\n" + \
		"Cluster number: " + str(self.clusterNum) + "\n" +	\
		"ImgWidth: " + str(self.imgWidth) + "\n" + \
		"ImgHeight: " + str(self.imgHeight) + "\n" \
		"DstClip path: " + self.dstClip + "\n" + \
		"DstLabel path: " + self.dstLabel + "\n" + \
		"+++++++++++++++++++++++++\n"

	def setOrigImgDim(self):
		self.imgWidth = self.imgWindow.shape[1]
		self.imgHeight = self.imgWindow.shape[0]

	def readContent(self):                                                      
		txtFile = open(self.srcLabel,"r")
		for content in iter(txtFile):
			contentN = content.rstrip('\n')
			#parsed format = "class id", "center point x coord", " center point y coord", "width", "height" 
			parsed = contentN.split()
			#(self, midX=0, midY=0, width=0, height=0, initiallyNorm=True)      # creates the Img object
			rectangle = Rectangle(parsed[1], parsed[2], parsed[3], parsed[4], True)

			self.rectsFetched.append(rectangle)
			#break # only do the first bounding box

		txtFile.close()

		#if (len(self.rectsFetched) > 1):
		#	print self.srcClip

	def denormalizeRectsFetched(self):
		for rectangle in self.rectsFetched:
			rectangle.denormalize(self.imgHeight, self.imgWidth)
			#if (len(self.rectsFetched) > 1):
			print rectangle

	def bboxAreaLimit(self):
		for rectangle in self.rectsFetched:
			if(rectangle.areaDeNorm < minBboxArea):
				return True
		return False

	def createClusterDir(self):
		clusterDirName = "/cluster" + str(self.clusterNum)
		#if (os.path.isdir(topDirName + "/images" + clusterDirName) is False):
		#	print "> " + clusterDirName + " doesn't exist! Creating " + clusterDirName
		#	os.makedirs(topDirName + "/images" + clusterDirName)
		#if (os.path.isdir(topDirName + "/labels" + clusterDirName) is False):
		#	os.makedirs(topDirName + "/labels" + clusterDirName)

	def setDstVars(self, index):		
		self.dstClip = topDirName + "/images" + "/cluster" + str(self. clusterNum) + "/" + self.baseClipName + "_" + str(index) + ".png"
		self.dstLabel = topDirName + "/labels" + "/cluster" + str(self. clusterNum) + "/" + self.baseClipName + "_" + str(index) + ".txt"

	def createCroppedImg(self, index):

		rectangle = self.rectsFetched[index]

		#check top and bot of image
		if ((rectangle.midYDeNorm-(cropDim/2)) < 0):
			startYcrop = 0
		elif ((rectangle.midYDeNorm+(cropDim/2)) > self.imgHeight):
			startYcrop = self.imgHeight - cropDim
		else:
			startYcrop = rectangle.midYDeNorm-(cropDim/2)

		#check left and right of image
		if ((rectangle.midXDeNorm-(cropDim/2)) < 0):
			startXcrop = 0
		elif ((rectangle.midXDeNorm+(cropDim/2)) > self.imgWidth):
			startXcrop = self.imgWidth - cropDim
		else:
			startXcrop = rectangle.midXDeNorm-(cropDim/2)

		self.cropWindow = self.imgWindow[startYcrop:(startYcrop+cropDim), startXcrop:(startXcrop+cropDim)]
		#cv2.imwrite(self.dstClip + "/crop720_" + str(index) + "_" + self.baseClip, self.cropWindow)
		self.currentCroppedClip = CropImage(startXcrop,startYcrop)
		#if (len(self.rectsFetched) > 1):
		#	print startXcrop
		#	print startYcrop			


	def findBboxesWithinCrop(self, index):
		for count in range(0,len(self.rectsFetched)):
			if ((self.rectsFetched[count].topLeftX >= self.currentCroppedClip.newOriginX) and (self.rectsFetched[count].botRightX <= (self.currentCroppedClip.newOriginX + cropDim)) \
			and (self.rectsFetched[count].topLeftY >= self.currentCroppedClip.newOriginY) and (self.rectsFetched[count].botRightY <= (self.currentCroppedClip.newOriginY + cropDim))):
				self.bboxesWithin.append(count)
				#if (len(self.rectsFetched) > 1):
				#	print count				

	def createNewBboxVals(self, index):
		for bboxNum in self.bboxesWithin:
			newCentXDeNorm = self.rectsFetched[bboxNum].midXDeNorm - self.currentCroppedClip.newOriginX
			newCentYDeNorm = self.rectsFetched[bboxNum].midYDeNorm - self.currentCroppedClip.newOriginY
			newBbox = Rectangle(newCentXDeNorm, newCentYDeNorm, self.rectsFetched[bboxNum].widthDeNorm, self.rectsFetched[bboxNum].heightDeNorm, False)
			self.rectsCropped.append(newBbox)

	def normalizeNewBbox(self, index):
		for rectangle in self.rectsCropped:
			rectangle.normalize(cropDim,cropDim)
			#print rectangle

	def saveNewLabel(self,index):
		savingFile = open(self.dstLabel + "/crop" + str(index) + "_" + self.baseLabel, "wb")
		for rectangle in self.rectsCropped:
			item = str(self.clusterNum) + " " + str(rectangle.midXNorm) + " " + str(rectangle.midYNorm) + " " + str(rectangle.widthNorm) + " " + str(rectangle.heightNorm)
			savingFile.write("%s\n" % item)
		savingFile.close()
		del self.bboxesWithin[:]
		del self.rectsCropped[:]

	def resizeCrop(self):
		r = float(resizeDim) / float (cropDim)
		dim = (resizeDim, int (cropDim * r))
		self.resizeWindow = cv2.resize(self.cropWindow, dim, interpolation = cv2.INTER_LINEAR)
		#cv2.imwrite(self.dstClip + "/crop" + str(index) + "_" + self.baseClip, self.resizeWindow)

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
    print "> Generating img list"

    tag1=".png" #
    nameList = []

    for root, dirs, files in os.walk(clipDirName, topdown=False):
        for name in files:
            if (name.rfind(tag1) != -1 ):
                nameList.append(os.path.join(root, name))          

    return naturalsort(nameList)
 
def saveNatSort(clipNames):
    savingFile = open(txtName, "wb")
    for name in clipNames:
        savingFile.write("%s\n" % name)
    savingFile.close()
# ##############################################################################################################################################################################
# #####################################################################################################################   MAIN CODE START


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Check for config file (checked)
parser = argparse.ArgumentParser(description='Img editor')

parser.add_argument('-s', type=str, default=''  , dest='clipSource' , help='top parent source directory name with jpg/JPEG images')

parsedArgs = parser.parse_args()

if (len(parsedArgs.clipSource) != 0 and parsedArgs.clipSource[len(parsedArgs.clipSource)-1] == '/'):
    clipSource = parsedArgs.clipSource[0:-1]
else:
    clipSource = parsedArgs.clipSource


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if (os.path.isdir(clipSource) is False): 
    print "> " + clipSource + " is not a valid path!"
    raise SystemExit

clipNames = generate_clipfile(clipSource)

# --------------------------------------------------------------------------------------------------------- if clipNames is empty, exit (checked)
if not clipNames:
    print "> Clip list is empty!"
    raise SystemExit


# --------------------------------------------------------------------------------------------------------- if clipNames is empty, exit (checked)
if not clipNames:
    print "> Clip list is empty!"
    raise SystemExit
#else:
#    saveNatSort(clipNames)

# ---------------------------------------------------------------- create top dir and subdirs in current dir of script
if (os.path.isdir(topDirName) is False):
	print "> " + topDirName + " doesn't exist! Creating " + topDirName
	os.makedirs(topDirName)
	os.makedirs(topDirName + "/images")
	os.makedirs(topDirName + "/labels")

# ----------------------------------------------------
for row in clipNames:

	checkClusterNum = "cluster" + str(currClusterNum)
	if (row.rfind(checkClusterNum) == -1 ):
		currClusterNum += 1

	currentClip = SrcImage(row,currClusterNum)
	currentClip.setOrigImgDim()
	currentClip.readContent()
	currentClip.denormalizeRectsFetched()

	#if (currentClip.bboxAreaLimit()):
	#	continue

	currentClip.createClusterDir()

	for index in range(0,len(currentClip.rectsFetched)):
		currentClip.setDstVars(index)
	print currentClip

#	    currentClip.createCroppedImg(index)
#	    currentClip.findBboxesWithinCrop(index)
#	    currentClip.createNewBboxVals(index)
#	    currentClip.normalizeNewBbox(index)
#	    currentClip.saveNewLabel(index)
#	    currentClip.resizeCrop()

	if (countup > 20):
		break
	else:
		countup += 1
	#print countup


