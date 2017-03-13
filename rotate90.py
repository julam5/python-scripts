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
txtName = "Rotated.txt"
sourceAddr = "."
dstDir = "./rotated90Labels"
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
	def __init__(self, midX=0, midY=0, width=0, height=0):      

		# normalized points for txt file
		self.midXNorm = float(midX)
		self.midYNorm = float(midY)
		self.widthNorm = float(width)
		self.heightNorm = float(height)


	# ------------------------------------------------------------------------- print rectangle info
	def __str__(self):
		return "============================== Rectangle\n" \
			"MidXNorm: "    + str(self.midXNorm) + "\n" \
			"MidYNorm: "    + str(self.midYNorm) + "\n" \
			"WidthNorm: "   + str(self.widthNorm) + "\n" \
			"HeightNorm: "  + str(self.heightNorm) + "\n" \
			"==============================\n" \
	# ------------------------------------------------------------------------- rotate points of rectangle by 90 degrees
	def rotateBy90(self):
		#swap height and width
		tempVar = self.heightNorm
		self.heightNorm = self.widthNorm
		self.widthNorm = tempVar

		#midX = midY and midY = 1-midX
		tempVar = 1-self.midXNorm
		self.midXNorm = self.midYNorm
		self.midYNorm = tempVar

# ============================================================================== SrcImage object
class SrcLabel():
	global sourceAddr, cropDim
# ------------------------------------------------------------------------- creates the Img object
	def __init__(self, srcLabel):   
		self.baseLabel = os.path.basename(srcLabel)
		self.srcLabel = sourceAddr + "/labels/" + srcLabel

		if (os.path.isdir(dstDir + "/" +os.path.dirname(srcLabel)) is False): 
			print "> " + dstDir + "/" + os.path.dirname(srcLabel) + " is not a valid path! Creating it now."
			os.makedirs(dstDir + "/" + os.path.dirname(srcLabel))

		self.clusterNum = -1
		self.dstLabel = dstDir + "/" + srcLabel

		self.rectsFetched = [] # holds bboxes from label txt (Rectangles)

# ------------------------------------------------------------------------- print image info
	def __str__(self):
		return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
		"Src Label path: " + self.srcLabel + "\n" + \
		"Dst Label path: " + self.dstLabel + "\n" + \
		 "+++++++++++++++++++++++++\n"

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

	def rotateLabels(self):
		for rectangle in self.rectsFetched:
			rectangle.rotateBy90()
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
	currentClip = SrcLabel(clip) 
	currentClip.readContent()

	if (len(currentClip.rectsFetched) > 0):
		#print currentClip
		currentClip.rotateLabels()
		currentClip.saveNewLabel()

#print len(clipNames)
