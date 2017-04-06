#!/usr/bin/env python

import ConfigParser
import os
import cv2
import numpy as np
import argparse
import ast
import copy
#-------------------------------------------------------------- from rosettacode
from itertools import groupby
from unicodedata import decomposition, name
from pprint import pprint as pp

####################################################################################################### GLOBAL VARS
index_imageList = 0
prev_index_imageList = 0
autosave = False

clipPathList = []
skipClipList = []
imageList = []


yellow = (0, 255, 255)
green = (0, 255, 0)
purple = (255, 0, 255)
red = (0, 0, 255)

ESC = 27
LEFT = 81
RIGHT = 83
UP = 82
DOWN = 84
ENTER = 10

drawing = False
####################################################################################################### FUNCTIONS
# ====================================================================================================== Natural sorting from rosettacode
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
    else:
        print "> Found directory: " + directoryName 

# ---------------------------------------------------------------- parse arguments passed
def getArguments():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-s', type=str, default=None, dest='srcClipDir', help='source clip dir path')

    parsedArgs = parser.parse_args()

    if (parsedArgs.srcClipDir == None):    
        print "> No /images directory path entered!"
        raise SystemExit

    if (parsedArgs.srcClipDir[-1] == '/'):
        srcClipDir = parsedArgs.srcClipDir[0:-1]
    else:
        srcClipDir = parsedArgs.srcClipDir

    srcClipDir = os.path.expanduser(srcClipDir)
    print "> Verifying source clip directory"
    ifNotDirExit(srcClipDir)

    return srcClipDir

# ---------------------------------------------------------------- generated list files
def listOfTags(directoryName,dotTag):
    print "> Generating list for " + dotTag + " tags" 
    
    nameList = []

    for root, dirs, files in os.walk(directoryName):
        for name in files:
            if (name.rfind(dotTag) != -1 ):
                nameList.append(os.path.join(root, name))

    if not nameList:
        print "> List of tags is empty!"
        raise SystemExit

    return naturalsort(nameList)

# ---------------------------------------------------------------- find and read configuration file
def configReader(baseClipDir):
    config = ConfigParser.ConfigParser()
    configFileName = baseClipDir + ".ini"

    if (os.path.isfile(configFileName)):
        print "> Found: " + configFileName
        config.read(configFileName)
        lastIndex = config.getint('Last_Session', 'last_pos')
        markedList = ast.literal_eval(config.get("Last_Session", "skip_list"))

    else:
        print "> Not Found: " + configFileName + " => Creating one at program's exit."
        lastIndex = 0
        markedList = []

    return lastIndex, markedList

# ---------------------------------------------------------------- print help    
def print_help():
    print "\n---------------- HELP BEG ------------------------"
    print "   MAIN KEY MAPPINGS:"
    print "   h = Show this key layout again"
    print "   Esc = Quit program"
    print "   Left Arrow = Move down 1 index"
    print "   Right Arrow = Move up 1 index"
    print "   d = Delete a rectangle"
    print "   r = Recover a rectangle"
    print "   s = Save all rectangles on screen"
    print "   m = Mark image as skipped"
    print "   Shift = Perform action w/o saving rectangles (for autosave=1)"
    print "   NOTE: Prompts for other keys will be asked in the terminal"
    print "\n   RECTANGLE COLORS:"
    print "   Green rectangles: Rectangles read from label file at startup"
    print "   Purple rectangles: Not saved in label file"
    print "   Yellow rectangles: Saved in label file"
    print "\n   AUTOSAVE:"
    print "   OFF: No progress is saved until user presses save key [s] on current image"
    print "   ON: Rectangles for an image are saved every time the user moves to another image or exits"
    print "       If user wishes to move on w/o saving, use Shift key before moving on or quiting"
    print "---------------- HELP END  ------------------------"

####################################################################################################### CLASSES
# =============================================================================================================== Rectangle object
class Rectangle():
    def __init__(self, topL=None, botR=None, midX=None, midY=None, width=None, height=None, color=None):      
        # denormalized points (x,y) = [0][1]
        self.topL = topL
        self.botR = botR

        # normalized points for txt file
        self.midX = midX
        self.midY = midY
        self.width = width
        self.height = height

        self.color = color

    # ------------------------------------------------------------------------- print image info
    def __str__(self):
        return "TopL: " + str(self.topL) + "\n" \
            "BotR: " + str(self.botR) + "\n" \
            "MidX: " + str(self.midX) + "\n" \
            "MidY: " + str(self.midY) + "\n" \
            "Width: " + str(self.width) + "\n" \
            "Height: " + str(self.height) + "\n" \
            "Color: " + str(self.color) + "\n" 

# ------------------------------------------------------------------------- normalize points of rectangle
    def normalize(self, imgRows, imgColmns):  
        self.midX   = "%.6f" %  ((((self.botR[0] - self.topL[0]) * 0.5) + self.topL[0]) / float(imgColmns))
        self.midY   = "%.6f" %  ((((self.botR[1] - self.topL[1]) * 0.5) + self.topL[1]) / float(imgRows))
        self.width  = "%.6f" %  ((((self.botR[0] - self.topL[0]))) / float(imgColmns))
        self.height = "%.6f" %  ((((self.botR[1] - self.topL[1]))) / float(imgRows))

    def denormalize(self, imgRows, imgColmns):
        # find normalized points
        topLx = float(self.midX) - (0.5 * float(self.width))
        topLy = float(self.midY) - (0.5 * float(self.height))
        botRx = float(self.midX) + (0.5 * float(self.width))
        botRy = float(self.midY) + (0.5 * float(self.height)) 

        # find denormalized points
        topLxDNorm = int(round(topLx * imgColmns))         
        topLyDNorm = int(round(topLy * imgRows))
        botRxDNorm = int(round(botRx * imgColmns))         
        botRyDNorm = int(round(botRy * imgRows))            

        # store rectangle points into rectangle object
        self.topL = (topLxDNorm,topLyDNorm)
        self.botR = (botRxDNorm,botRyDNorm)

class Image():
	global imgWindow
    # ------------------------------------------------------------------------- creates the Img object
	def __init__(self, srcName):
		self.srcClip = srcName
		self.srcLabel = (srcName[0:-4] + ".txt").replace("images", "labels")

		# rectangle info
		self.clusterid = -1
		self.rectsSaved = []
		self.rectsDel = []

		self.marked = False

		self.img = cv2.imread(self.srcClip)
		self.imgWidth = self.img.shape[1]
		self.imgHeight = self.img.shape[0]

		if os.path.isfile(self.srcLabel) and os.stat(self.srcLabel).st_size != 0:
			self.readContent()
		#else:
		#	print "No label found"
    # ------------------------------------------------------------------------- print image info
	def __str__(self):
		return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
		"Clip  path: " + self.srcClip + "\n" + \
		"Label path: " + self.srcLabel + "\n" + \
		"Cluster number: " + str(self.clusterid) + "\n" +  \
		"ImgWidth: " + str(self.imgWidth) + "\n" + \
		"ImgHeight: " + str(self.imgHeight) + "\n" + \
		"+++++++++++++++++++++++++" + "\n"

    # ------------------------------------------------------------------------- read existing txt label
	def readContent(self):                                                      
		txtFile = open(self.srcLabel,"r")

		for content in iter(txtFile):
			contentN = content.rstrip('\n')
			#parsed format = "class id", "center point x coord", " center point y coord", "width", "height" 
			parsed = contentN.split()
			self.clusterid = parsed[0]
			#(topL=None, botR=None, midX=None, midY=None, width=None, height=None, color=None):      # creates the Img object
			rectangle = Rectangle(None, None, parsed[1], parsed[2], parsed[3], parsed[4], red)
			rectangle.denormalize(self.imgHeight,self.imgWidth)
			self.rectsSaved.append(rectangle)
			print rectangle

	   	txtFile.close()
    # ------------------------------------------------------------------------- draw rectangles onto window
	def drawRects(self):            
		for rect in self.rectsSaved:
			cv2.rectangle(imgWindow, rect.topL, rect.botR, rect.color, 1)

####################################################################################################### MAIN CODE

srcClipDir = getArguments()

clipPathList = listOfTags(srcClipDir,".png")

index_imageList, skipClipList = configReader(os.path.basename(srcClipDir))
prev_index_imageList = index_imageList

for clipPath in clipPathList:
    newClip = Image(clipPath)
    if (skipClipList) and (newClip in skipClipList):
        newClip.marked = True
    imageList.append(newClip)

###################################################################
autosave = int(raw_input("==> Enable autosave? (0=no,1=yes): "))
print "> Autosave: " + str(bool(autosave))

################################################################### image viewer
cv2.namedWindow('ImgWindow', cv2.WINDOW_NORMAL)
# --------------------------------------------------------------------------------------------------------------- Infinite loop till Esc exit
print "> Entered viewer"
print_help()
imgWindow = imageList[index_imageList].img
imageList[index_imageList].drawRects()

while True:

    # ------------------------------------------------------------------------- print info only if moved to new image (checked)
    if prev_index_imageList != index_imageList:
        imgWindow = imageList[index_imageList].img
        imageList[index_imageList].drawRects()
        print "\n=======> CURRENT IMAGE [ " + os.path.basename(imageList[index_imageList].srcClip) + " ]"
        print imageList[index_imageList]

    # ------------------------------------------------------------------------- draw rectangles and show imgWindow matrix (picture)
    cv2.imshow('ImgWindow',imgWindow)
    
    # ------------------------------------------------------------------------- polls here for refresh img or a keypress
    key = cv2.waitKey(30) & 0xFF
    #print key

    # ------------------------------------------------------------------------- add rectangles from refPt list into img's rectangles list
    prev_index_imageList = index_imageList

    # ------------------------------------------------------------------------- keypress options
    # ------------------------------------------------ if Esc key is pressed
    if key == ESC:
    	print "> Bye!\n"
    	break

    # ------------------------------------------------ if left arrow key is pressed
    elif key == LEFT: 
        if index_imageList == 0:
            index_imageList = len(imageList) - 1
        else:
            index_imageList -= 1

    # ------------------------------------------------ if right arrow key is pressed
    elif key == RIGHT:
        if index_imageList == len(imageList) - 1:
            index_imageList = 0
        else:
            index_imageList += 1

    # ------------------------------------------------ to delete a rectangle
   

cv2.destroyAllWindows()
