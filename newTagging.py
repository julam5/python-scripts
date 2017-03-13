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

# =============================================================================================================== Global Vars
imgNum = 0
clipNames = []
markedList = []

dstDir = "."

imageList = []
refPt = []

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

prevSess = 0

imgNumPrv = -1
currentNumRects = 0

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
# =============================================================================================================== Mouse Callback
def draw_n_add(event, x, y, flags, param):

    global refPt, imgWindow, currentNumRects, purple, red, drawing, imgNum
 
	# if the left mouse button was clicked, record the starting (x, y) coordinates 
    if event == cv2.EVENT_LBUTTONDOWN:
        if x < 0:
            x = 0
        if x > imgWindow.shape[1]:
            x = imgWindow.shape[1]

        if y < 0:
            y = 0
        if y > imgWindow.shape[0]:
            y = imgWindow.shape[0]

        refPt.append((x, y))
        drawing = True
 
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
    #        if x < 0:
     #           x = 0
      #      if x > imgWindow.shape[1]:
       #         x = imgWindow.shape[1]

    #        if y < 0:
     #           y = 0
      #      if y > imgWindow.shape[0]:
       #         y = imgWindow.shape[0]            
            lastPt = len(refPt) - 1
            imgWindow = cv2.imread(imageList[imgNum].imgName)
            cv2.rectangle(imgWindow, refPt[lastPt], (x,y), purple, 1)

	# check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if x < 0:
            x = 0
        if x > imgWindow.shape[1]:
            x = imgWindow.shape[1]

        if y < 0:
            y = 0
        if y > imgWindow.shape[0]:
            y = imgWindow.shape[0]        
        refPt.append((x, y))
        lastTwoPts = len(refPt) - 2
        
        ix = refPt[lastTwoPts][0]
        iy = refPt[lastTwoPts][1]
        fx = refPt[lastTwoPts+1][0]
        fy = refPt[lastTwoPts+1][1]

        widthT = abs(fx - ix)
        heightT = abs(fy - iy)

        if (widthT > 9) and (heightT > 9):
            #quadrant 1
            if (ix > fx) and (iy > fy):
                newTopL = (fx,fy)
                newBotR = (ix,iy)

            #quadrant 4
            elif (fx > ix) and (fy > iy):
                newTopL = (ix,iy)
                newBotR = (fx,fy)

            #quadrant 2
            elif (fx > ix):
                newTopL = (ix,fy)
                newBotR = (fx,iy)

            #quadrant 3
            else:
                newTopL = (fx,iy)
                newBotR = (ix,fy)

            refPt.pop()
            refPt.pop()
            refPt.append(newTopL)
            refPt.append(newBotR)
            print newTopL
            print newBotR
            currentNumRects += 1

        else:
            refPt.pop()
            refPt.pop()
            imgWindow = cv2.imread(imageList[imgNum].imgName)

# =============================================================================================================== Mouse Callback
# =============================================================================================================== Print Messages
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
# =============================================================================================================== Print Messages
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
 
# =============================================================================================================== Generate clipFile.txt
# #################################################################################################################################    CLASSES
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

# =============================================================================================================== Image object
class Image():
    global refPt, yellow, green, purple, red, UP, DOWN, ENTER
    
    # ------------------------------------------------------------------------- creates the Img object
    def __init__(self, imgName, destName):                                         
        self.imgName = imgName
        self.baseName = os.path.basename(imgName)

        stripped1 = (os.path.basename(imgName)).rstrip('.png')
        dashIndex = stripped1.rfind('-')

        subDir = os.path.dirname(imgName)
        lastSlashIndex = subDir.rfind('/')

        self.txtName = destName + "/labels" +'/' + subDir[lastSlashIndex+1:] + '/' + stripped1 + '.txt'


        self.leafDirPath = os.path.dirname(self.txtName)

        # rectangle info
        self.classid = 2
        self.rectsNorm = []
        self.rectsSaved = []
        self.rectsDel = []

        self.marked = False

    # ------------------------------------------------------------------------- print image info
    def __str__(self):
        return "Img Name: " + self.imgName + "\n" \
               "Txt Name: " + self.txtName + "\n" \
               "Leaf Name: " + self.leafDirPath + "\n" 

    # ------------------------------------------------------------------------- read existing text file and stores normalized points
    def readContent(self):                                                      
        txtFile = open(self.txtName,"r")

        for content in iter(txtFile):
            contentN = content.rstrip('\n')
            #parsed format = "class id", "center point x coord", " center point y coord", "width", "height" 
            parsed = contentN.split()
            #(topL=None, botR=None, midX=None, midY=None, width=None, height=None, color=None):      # creates the Img object
            rectangle = Rectangle(None, None, parsed[1], parsed[2], parsed[3], parsed[4], green)

            self.rectsNorm.append(rectangle)
        
        txtFile.close()

    # ------------------------------------------------------------------------- denormalizes all read in points and move them to rectsSaved container
    def addRectsNorm(self, imgRows, imgColmns):  
        for rectNorm in self.rectsNorm:
            rectNorm.denormalize(imgRows, imgColmns)
            self.rectsSaved.append(rectNorm)

        # clear list of normalized rectangles
        del self.rectsNorm[:]

    # ------------------------------------------------------------------------- draw rectangles onto window
    def drawRects(self):            
        label = 0
        for rect in self.rectsSaved:
            cv2.rectangle(imgWindow, rect.topL, rect.botR, rect.color, 1)
            label += 1

    # ------------------------------------------------------------------------- draw numbers onto window
    def drawNums(self):
        label = 0
        for rect in self.rectsSaved:
            cv2.putText(imgWindow, str(label), rect.botR, cv2.FONT_HERSHEY_COMPLEX, 1, red,2,1)
            label += 1

    # ------------------------------------------------------------------------- draw skipped onto window
    def drawSkipped(self):
        cv2.putText(imgWindow, "SKIPPED", (460,350), cv2.FONT_HERSHEY_COMPLEX, 2, red,3,1)

    # ------------------------------------------------------------------------- add rectangles from refPt
    def addRects(self, imgRows, imgColmns):             

        index = 0        
        while index < (len(refPt)-1):
            rect = Rectangle(refPt[index], refPt[index+1], None, None, None, None, purple)
            rect.normalize(imgRows, imgColmns)
            self.rectsSaved.append(rect)
            index += 2

    # ------------------------------------------------------------------------- removes one rectangle of user's choice
    def removeRect(self):           
        if len(self.rectsSaved) == 1:
            self.rectsDel.append(self.rectsSaved.pop())
            print "> Deleted last rectangle"
        else:        
            print "\n==> Delete which rectangle? (Enter to confirm or c to cancel)"
            print "> Use up and down arrows to choose a number"

            index = 0
            indexPrev = -1
            while True:
                if index != indexPrev:                
                    print "  Currently selected: " + str(index)

                indexPrev = index
                k = cv2.waitKey(0) & 0xFF
            
                if k == ENTER:
                    break

                elif k == ord("c"):
                    index = -1
                    break
        
                elif k == UP and (index < (len(self.rectsSaved)-1)):
                    index += 1

                elif k == DOWN and index != 0:
                    index -= 1

            if index != -1:
                self.rectsDel.append(self.rectsSaved.pop(index))
                print "> Deleted"
            
            else:
                print "> Cancelled delete"
    
    # ------------------------------------------------------------------------- recovers the last deleted rectangle
    def reAddRect(self):        
        rect = self.rectsDel.pop()
        rect.color = purple
        self.rectsSaved.append(rect)
        print "> Recovered last rectangle deleted"

    # ------------------------------------------------------------------------- save all rectangles in rectSaved container
    def saveProg(self):
        savingFile = open(self.txtName, "wb")
        for rect in self.rectsSaved:
            item = str(self.classid) + " " + str(rect.midX) + " " + str(rect.midY) + " " + str(rect.width) + " " + str(rect.height)
            savingFile.write("%s\n" % item)            
            rect.color = yellow
      
        savingFile.close()
        print "> Saved!"

    # ------------------------------------------------------------------------- mark image as skipped
    def markImg(self):
        self.marked = True
        if os.path.isfile(self.txtName):
            os.remove(self.txtName)
        for rect in self.rectsSaved:         
            rect.color = purple

    # ------------------------------------------------------------------------- unmark image as skipped
    def unmarkImg(self):
        self.marked = False

# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
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

if (clipSource == ''):    
    clipSource = raw_input("> Enter clip directory's path (use . and .. if necessary): ")


# ---------------------------------------------------------------------------------------------------------- check if image directory exists (checked)
if (os.path.isdir(clipSource) is False): 
    print "> " + clipSource + " is not a valid path!"
    raise SystemExit

# example :: clipSource = "./images/clip#_****"

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Check for config file (checked)
configFileName = os.path.basename(clipSource) + ".ini"

config = ConfigParser.ConfigParser()

if (os.path.isfile(configFileName)):
    print "> Found " + configFileName
    config.read(configFileName)

    #set variables from config file
    lastDir = config.get('Last_Session', 'last_folder')
    imgNum = config.getint('Last_Session', 'last_pos')
    markedList = ast.literal_eval(config.get("Last_Session", "skip_list"))
    
else:
    print "Did not find config file. Creating one at program's exit."

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

clipNames = generate_clipfile(clipSource)

# --------------------------------------------------------------------------------------------------------- if clipNames is empty, exit (checked)
if not clipNames:
    print "> Clip list is empty!"
    raise SystemExit
#else:
#    print clipNames
# --------------------------------------------------------------------------------------------------------------- create image array
for image in clipNames:
    pic = Image(image,dstDir)
    if (markedList) and (image in markedList):
        pic.marked = True
    print pic
    #imageList.append(pic)
    #if os.path.isfile(pic.txtName) and os.stat(pic.txtName).st_size != 0: # enable only if checking labels
	#   imageList.append(pic)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Enable autosave?
#autosave = int(raw_input("==> Enable autosave? (0=no,1=yes): "))
#print "> Autosave: " + str(bool(autosave))


