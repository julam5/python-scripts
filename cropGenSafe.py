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
        else:
            self.midXNorm = 0
            self.midYNorm = 0
            self.widthNorm = 0
            self.heightNorm = 0

            self.midXDeNorm = int(midX)
            self.midYDeNorm = int(midY)
            self.widthDeNorm = int(width)
            self.heightDeNorm = int(height)

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

# ============================================================================== Image object
class Image():
    global sourceAddr
# ------------------------------------------------------------------------- creates the Img object
    def __init__(self, srcClip, clusterNum):                                         
        self.srcClip = sourceAddr + "/images/" + srcClip
        self.srcLabel = sourceAddr + "/labels/" + srcClip.rstrip('.png') + ".txt"
        self.clusterNum = clusterNum
        self.rectsFetched = []
        self.rectsCropped = []
        self.imgWidth = 0
        self.imgHeight = 0

# ------------------------------------------------------------------------- print image info
    def __str__(self):
        return "+++++++++++++++++++++++++++++++ Image\n" + \
        "Clip path: " + self.srcClip + "\n" + \
        "Cluster number: " + str(self.clusterNum) + "\n" +  \
        "Label path: " + self.srcLabel + "\n" + \
        "ImgWidth: " + str(self.imgWidth) + "\n" + \
        "ImgHeight: " + str(self.imgHeight) + "\n" \
        + "+++++++++++++++++++++++++\n"

    def setOrigImgDim(self):
        imgWindow = cv2.imread(self.srcClip)
        self.imgWidth = imgWindow.shape[1]
        self.imgHeight = imgWindow.shape[0]

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
            print rectangle

# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- take in arguments
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='', dest='csvSource', help='orig text file')
#parser.add_argument('-n', type=int, default=0, dest='numClusters', help='number of clusters')

parsedArgs = parser.parse_args()

# ---------------------------------------------------- check csvSource
if (len(parsedArgs.csvSource) == 0 or not os.path.isfile(parsedArgs.csvSource)):
    print "> csv source is invalid!"
    raise SystemExit
else:
    addrCsvSource = parsedArgs.csvSource

print "\n> Using " + addrCsvSource + " as text source"

####################################
# ---------------------------------------------------- check number of clusters
#if (parsedArgs.numClusters == 0):
#    numClusters = int(raw_input("==> Enter number of clusters: "))
#else:
#    numClusters = parsedArgs.numClusters
#
#print "\n> Number of clusters is " + str(numClusters)
####################################

# ---------------------------------------------------------------- create top dir and subdirs in current dir of script
if (os.path.isdir(topDirName) is False):
    print "> " + topDirName + " doesn't exist! Creating " + topDirName
    os.makedirs(topDirName)
####################################
    #for numCount in range(0,numClusters):
        #print topDirName + "/cluster" + str(numCount)
        #print topDirName + "/cluster" + str(numCount) + "/images"
        #print topDirName + "/cluster" + str(numCount) + "/labels"

    #   os.makedirs(topDirName + "/cluster" + str(numCount))
    #   os.makedirs(topDirName + "/cluster" + str(numCount) + "/images")
    #   os.makedirs(topDirName + "/cluster" + str(numCount) + "/labels")
#####################################

# ----------------------------------------------------
with open(addrCsvSource, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        #print sourceAddr + row[0] + " " + row[1]
        currentClip = Image(row[0],row[1])
        currentClip.setOrigImgDim()
        #print currentClip
        currentClip.readContent()
        currentClip.denormalizeRectsFetched()
        break





