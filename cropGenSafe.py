#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
import csv
import numpy as np
import cv2
# #######################################################################################   Global Vars
sourceAddr = "/home/justin/Pictures/imgLabeling"
topDirName = "./yolo"
cropDim = 448
countup = 0
minBboxArea = 32 * 32

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

        self.midXDeNorm     = int(round(self.midXNorm * imgColmns))
        self.midYDeNorm     = int(round(self.midYNorm * imgRows))
        self.widthDeNorm    = int(round(self.widthNorm * imgColmns))
        self.heightDeNorm   = int(round(self.heightNorm * imgRows))

        self.areaDeNorm = self.widthDeNorm * self.heightDeNorm

# ============================================================================== CropImage object
class CropImage():
    def __init__(self,startXcrop,startYcrop):
        self.newOriginX = startXcrop
        self.newOriginY = startYcrop


# ============================================================================== SrcImage object
class SrcImage():
    global sourceAddr, cropDim, countup, minBboxArea
# ------------------------------------------------------------------------- creates the Img object
    def __init__(self, srcClip, clusterNum):   
        self.dirClip = os.path.dirname(srcClip)                                      
        self.srcClip = sourceAddr + "/images/" + srcClip
        self.srcLabel = sourceAddr + "/labels/" + srcClip.rstrip('.png') + ".txt"
        self.dstClip = None
        self.dstLabel = None
        self.clusterNum = clusterNum
        self.rectsFetched = []
        self.clipsCropped = []
        self.rectsCropped = []
        self.imgWidth = 0
        self.imgHeight = 0
        self.imgWindow = cv2.imread(self.srcClip)
        self.cropWindow = None
        #cv2.imwrite("Original_" + str(countup) +".png", self.imgWindow)

# ------------------------------------------------------------------------- print image info
    def __str__(self):
        return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
        "Clip path: " + self.srcClip + "\n" + \
        "Cluster number: " + str(self.clusterNum) + "\n" +  \
        "Label path: " + self.srcLabel + "\n" + \
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
            #(self, midX=0, midY=0, width=0, height=0, initiallyNorm=True)      # creates the Img object
            rectangle = Rectangle(parsed[1], parsed[2], parsed[3], parsed[4], True)

            self.rectsFetched.append(rectangle)
            break # only do the first bounding box

        txtFile.close()

    def denormalizeRectsFetched(self):
        for rectangle in self.rectsFetched:
            rectangle.denormalize(self.imgHeight, self.imgWidth)
            #print rectangle

    def bboxAreaLimit(self):
        for rectangle in self.rectsFetched:
            if(rectangle.areaDeNorm < minBboxArea):
                return True
        return False

    def createClusterDir(self):
        clusterDirName = topDirName + "/cluster" + self.clusterNum
        if (os.path.isdir(clusterDirName) is False):
            print "> " + clusterDirName + " doesn't exist! Creating " + clusterDirName
            os.makedirs(clusterDirName)
            os.makedirs(clusterDirName + "/images")
            os.makedirs(clusterDirName + "/labels")

        if (os.path.isdir(clusterDirName + "/images" + "/" + self.dirClip) is False):
            os.makedirs(clusterDirName + "/images" + "/" + self.dirClip)    
            os.makedirs(clusterDirName + "/labels" + "/" + self.dirClip)

        self.dstClip = clusterDirName + "/images" + "/" + self.dirClip
        self.dstLabel = clusterDirName + "/labels" + "/" + self.dirClip
        #print self.dstClip
        #print self.dstLabel

    def createCroppedImg(self):
        for rectangle in self.rectsFetched:
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
            croppedImg = CropImage(startXcrop,startYcrop)
            self.clipsCropped.append(croppedImg)
            #cv2.imwrite("Cropped_" + str(countup) +".png", self.cropWindow)
            #print startXcrop
            #print startYcrop

    def createNewBboxVals(self):
        for index in range(0,len(self.rectsFetched)):
            newCentXDeNorm = self.rectsFetched[index].midXDeNorm - self.clipsCropped[index].newOriginX
            newCentYDeNorm = self.rectsFetched[index].midYDeNorm - self.clipsCropped[index].newOriginY
            #print newCentX
            #print newCentY
            #newBbox = self.cropWindow[(newCentY-self.rectsFetched[index].heightDeNorm/2):(newCentY+self.rectsFetched[index].heightDeNorm/2), (newCentX-self.rectsFetched[index].widthDeNorm/2):(newCentX+self.rectsFetched[index].widthDeNorm/2)]
            #cv2.imwrite("BBox_" + str(countup) +".png", newBbox)
            newBbox = Rectangle(newCentXDeNorm, newCentYDeNorm, self.rectsFetched[index].widthDeNorm, self.rectsFetched[index].heightDeNorm, False)
            self.rectsCropped.append(newBbox)

    def normalizeNewBboxes(self):
        for rectangle in self.rectsCropped:
            rectangle.normalize(cropDim,cropDim)
            #print rectangle

    def saveNewLabels(self):
        savingFile = open("Cropped_" + str(countup) +".txt", "wb")
        for rectangle in self.rectsCropped:
            item = str(self.clusterNum) + " " + str(rectangle.midXNorm) + " " + str(rectangle.midYNorm) + " " + str(rectangle.widthNorm) + " " + str(rectangle.heightNorm)
            savingFile.write("%s\n" % item)
            break

        savingFile.close()

# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- take in arguments
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='', dest='csvSource', help='orig text file')
parsedArgs = parser.parse_args()

# ---------------------------------------------------- check csvSource
if (len(parsedArgs.csvSource) == 0 or not os.path.isfile(parsedArgs.csvSource)):
    print "> csv source is invalid!"
    raise SystemExit
else:
    addrCsvSource = parsedArgs.csvSource

print "\n> Using " + addrCsvSource + " as text source"

# ---------------------------------------------------------------- create top dir and subdirs in current dir of script
if (os.path.isdir(topDirName) is False):
    print "> " + topDirName + " doesn't exist! Creating " + topDirName
    os.makedirs(topDirName)

# ----------------------------------------------------
with open(addrCsvSource, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        currentClip = SrcImage(row[0],row[1])
        currentClip.setOrigImgDim()
        #print currentClip
        currentClip.readContent()
        currentClip.denormalizeRectsFetched()
        if (currentClip.bboxAreaLimit()):
            continue
        currentClip.createClusterDir()
        currentClip.createCroppedImg()
        currentClip.createNewBboxVals()
        currentClip.normalizeNewBboxes()
        currentClip.saveNewLabels()

        if (countup > 5):
            break
        else:
            countup += 1





