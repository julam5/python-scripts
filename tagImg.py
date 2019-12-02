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
        
        stripped1 = (os.path.basename(imgName)).rstrip('.png')
        dashIndex = stripped1.rfind('-')

        subDir = os.path.dirname(imgName)
        lastSlashIndex = subDir.rfind('/')

        self.txtName = destName.rstrip('.png') + ".txt" #+ '/' + subDir[lastSlashIndex+1:] + '/' + stripped1 + '.txt'


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
            rectangle = Rectangle(None, None, parsed[1], parsed[2], parsed[3], parsed[4], red)

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
# =============================================================================================================== Global Vars
imgNum = 0
clipNames = []
markedList = []

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
# --------------------------------------------------------------------------------------------------------------- Check for config file (checked)
config = ConfigParser.ConfigParser()

if (os.path.isfile('currentConfig.ini')):
    print "> Found previous config file."
    config.read('currentConfig.ini')
    lastDir = config.get('Last_Session', 'last_folder')
    print "> Previous session: " + lastDir

    if (clipSource != ''):
        prevSess =  (clipSource == lastDir)             #int(raw_input("Restore prev session? (0=no,1=yes): "))
    else:
        prevSess = int(raw_input("==> Restore prev session? (0=no,1=yes): "))

    if not prevSess:
        print "> Not using prev configuration"
        prevFolder = config.get('Last_Session', 'last_folder')
        prevPos = config.getint('Last_Session', 'last_pos')
        prevClips = ast.literal_eval(config.get("Last_Session", "clip_list"))
        prevMarked = ast.literal_eval(config.get("Last_Session", "skip_list"))

        config = ConfigParser.RawConfigParser()

        config.add_section('Last_Session')
        config.set('Last_Session', 'last_folder', prevFolder)
        config.set('Last_Session', 'last_pos', prevPos)
        config.set('Last_Session', 'clip_list', prevClips)
        config.set('Last_Session', 'skip_list', prevMarked)

        with open( os.path.basename(config.get('Last_Session', 'last_folder')) +'.ini', 'wb') as configfile:
            config.write(configfile)

else:
    print "Did not find config file. Creating one at program's exit."

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- if config file will be used (checked)
if prevSess:
    imgNum = config.getint('Last_Session', 'last_pos')
    clipNames = ast.literal_eval(config.get("Last_Session", "clip_list"))
    markedList = ast.literal_eval(config.get("Last_Session", "skip_list"))

# --------------------------------------------------------------------------------------------------------------- if config file will NOT be used (checked)
else:
    if (clipSource == ''):    
        clipSource = raw_input("> Enter clip directory's path (use . and .. if necessary): ")

    # ---------------------------------------------------------------------------------------------------------- check if image directory exists (checked)
    if (os.path.isdir(clipSource) is False): 
        print "> " + clipSource + " is not a valid path!"
        raise SystemExit
    
    clipNames = generate_clipfile(clipSource)

    # --------------------------------------------------------------------------------------------------------- if clipNames is empty, exit (checked)
    if not clipNames:
        print "> Clip list is empty!"
        raise SystemExit

# --------------------------------------------------------------------------------------------------------------- create image array
for image in clipNames:
    label = image.replace("images", "labels")
    pic = Image(image,label)
    if (markedList) and (image in markedList):
        pic.marked = True
    imageList.append(pic)
    #if os.path.isfile(pic.txtName) and os.stat(pic.txtName).st_size != 0: # enable only if checking labels
	#   imageList.append(pic)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Enable autosave?
autosave = int(raw_input("==> Enable autosave? (0=no,1=yes): "))
print "> Autosave: " + str(bool(autosave))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Finding exisiting labels (checked)
for image in imageList:
 
    if (os.path.isdir(image.leafDirPath) is False):
        print "> " + image.leafDirPath + " doesn't exist in current directory! Creating " + image.leafDirPath + " directory"
        os.makedirs(image.leafDirPath)

    else:
        if os.path.isfile(image.txtName) and os.stat(image.txtName).st_size != 0:
            image.readContent()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Running image editor
imgLim = len(imageList)


cv2.namedWindow('ImgWindow', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('ImgWindow', draw_n_add)

# --------------------------------------------------------------------------------------------------------------- Infinite loop till Esc exit
print "> Entered viewer"
print_help()

while True:

    # ------------------------------------------------------------------------- print info only if moved to new image (checked)
    if imgNum != imgNumPrv:
        imgWindow = cv2.imread(imageList[imgNum].imgName)
        print "\n=======> CURRENT IMAGE [ " + os.path.basename(imageList[imgNum].imgName) + " ]"
        print imageList[imgNum]

    # ------------------------------------------------------------------------- denormalize any rectangles left in img's label file
    if imageList[imgNum].rectsNorm:
        imageList[imgNum].addRectsNorm(imgWindow.shape[0], imgWindow.shape[1])

    # ------------------------------------------------------------------------- draw rectangles and show imgWindow matrix (picture)
    currentNumRects = len(imageList[imgNum].rectsSaved)
    if not imageList[imgNum].marked:
        imageList[imgNum].drawRects()    
    if imageList[imgNum].marked:
        imageList[imgNum].drawSkipped()  
    cv2.imshow('ImgWindow',imgWindow)
    
    # ------------------------------------------------------------------------- polls here for refresh img or a keypress
    key = cv2.waitKey(30) & 0xFF
    #print key

    # ------------------------------------------------------------------------- add rectangles from refPt list into img's rectangles list
    imgNumPrv = imgNum
    if len(refPt) > 1:
        imageList[imgNum].addRects(imgWindow.shape[0], imgWindow.shape[1]) 
        del refPt[:]  

    # ------------------------------------------------------------------------- keypress options
    # ------------------------------------------------ if Esc key is pressed
    if key == ESC:
        if bool(autosave):
            if (not imageList[imgNum].marked):
                imageList[imgNum].saveProg()
            print "> Bye!\n"
            break

        else:
            print '==> Do you really wish to quit? (press Esc for Yes)'
            key = cv2.waitKey(0) & 0xFF
            if key == 27:
                print "> Bye!\n"
                break
        print "> Cancelled quitting"

    # ------------------------------------------------ if left arrow key is pressed
    elif key == LEFT: 
        if bool(autosave and not imageList[imgNum].marked):
            imageList[imgNum].saveProg()

        if imgNum == 0:
            imgNum = imgLim - 1
        else:
            imgNum -= 1

    # ------------------------------------------------ if right arrow key is pressed
    elif key == RIGHT:
        if bool(autosave and not imageList[imgNum].marked):
            imageList[imgNum].saveProg()

        if imgNum == imgLim - 1:
            imgNum = 0
        else:
            imgNum += 1

    # ------------------------------------------------ to delete a rectangle
    elif key == ord("d"):
        imageList[imgNum].drawNums()
        cv2.imshow('ImgWindow',imgWindow)
        if (imageList[imgNum].rectsSaved):
            imageList[imgNum].removeRect()
            imgWindow = cv2.imread(imageList[imgNum].imgName)

    # ------------------------------------------------ to recover a rectangle
    elif key == ord("r"):
        if (imageList[imgNum].rectsDel and not imageList[imgNum].marked):
            imageList[imgNum].reAddRect()

    # ------------------------------------------------ to save all current rectangles
    elif key == ord("s"):
        if not imageList[imgNum].marked:
            imageList[imgNum].saveProg()

    # ------------------------------------------------ shift mode
    elif key == 226 or key == 225:
        print "> Shift key pressed, waiting for next key. (Valid keys: Left, Right, Esc)"
        key = cv2.waitKey(0) & 0xFF

        if key == LEFT: #print "Shift + Left"

            if imgNum == 0:
                imgNum = imgLim - 1
            else:
              imgNum -= 1

        elif key == RIGHT: #print "Shift + Right"

            if imgNum == imgLim - 1:
                imgNum = 0
            else:
                imgNum += 1

        elif key == ESC: # Shift Exit
            print "> Bye!\n"
            break

        else:
            print "> No valid keypress combination with shift, leaving shift key wait"

    # ------------------------------------------------ print help
    elif key == ord("h"):
        print_help()     

    # ------------------------------------------------ print help
    elif key == ord("m"):
        if imageList[imgNum].marked:
            imageList[imgNum].unmarkImg()
            print "> Unmarking image"
            imgWindow = cv2.imread(imageList[imgNum].imgName)
        else:
            imageList[imgNum].markImg()
            print "> Marking image"
            imgWindow = cv2.imread(imageList[imgNum].imgName)

cv2.destroyAllWindows()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
config = ConfigParser.RawConfigParser()

config.add_section('Last_Session')
config.set('Last_Session', 'last_folder', os.path.dirname(clipNames[0]))
config.set('Last_Session', 'last_pos', imgNum)
config.set('Last_Session', 'clip_list', clipNames)

del markedList[:]
for image in imageList:
    if image.marked:
        markedList.append(image.imgName)
config.set('Last_Session', 'skip_list', markedList)

with open('currentConfig.ini', 'wb') as configfile:
    config.write(configfile)

