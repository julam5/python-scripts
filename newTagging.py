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
# =============================================================================================================== GLOBAL VARS
index_imageList = 0
autosave = False

clipPathList = []
skipClipList = []
imageList = []



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

# ---------------------------------------------------------------- check if path is directory
def ifNotDirExit(directoryName):
    if (os.path.isdir(directoryName) is False): 
        print "> " + directoryName + " is not a valid directory!"
        raise SystemExit
    else:
        print "> Found directory: " + directoryName 

# ---------------------------------------------------------------- parse arguments passed
def getArguments():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-s', type=str, default='', dest='srcClipDir', help='source clip dir path')

    parsedArgs = parser.parse_args()

    if (len(parsedArgs.srcClipDir) != 0 and parsedArgs.srcClipDir[-1] == '/'):
        srcClipDir = parsedArgs.srcClipDir[0:-1]
    else:
        srcClipDir = parsedArgs.srcClipDir

    if (srcClipDir == ''):    
        srcClipDir = raw_input("> Enter source clip folder path (use . and .. if necessary): ")

    srcClipDir = os.path.expanduser(srcClipDir)
    ifNotDirExit(srcClipDir)

    srcLabelDir = srcClipDir.replace("images", "labels")
    ifNotDirExit(srcLabelDir) 

    return srcClipDir, srcLabelDir

# ---------------------------------------------------------------- generated list files
def listOfTags(dirName,dotTag):
    print "> Generating list for " + dotTag + " tags" 
    
    nameList = []

    for root, dirs, files in os.walk(dirName):
        for name in files:
            if (name.rfind(dotTag) != -1 ):
                nameList.append(os.path.join(root, name))          

    return naturalsort(nameList)

def configReader(baseClipDir):
    config = ConfigParser.ConfigParser()
    configFileName = baseClipDir+".ini"

    if (os.path.isfile(configFileName)):
        print "> Found " + configFileName
        config.read(configFileName)
        lastIndex = config.getint('Last_Session', 'last_pos')

        markedList = ast.literal_eval(config.get("Last_Session", "skip_list"))

    else:
        print "> Did not find " + configFileName + "; Creating one at program's exit."

    return lastIndex, markedList



class ImageProperties():
    global sourceAddr, cropDim, minBboxArea, resizeDim
    # ------------------------------------------------------------------------- creates the Img object
    def __init__(self, srcName, clusterNum):   
        self.srcClip = srcName[0:-4] + ".png"
        self.srcLabel = srcName[0:-4] + ".txt"



    # ------------------------------------------------------------------------- print image info
    def __str__(self):
        return "+++++++++++++++++++++++++++++++ SrcImage\n" + \
        "Clip path: " + self.srcClip + "\n" + \
        "Label path: " + self.srcLabel + "\n" + \
        "+++++++++++++++++++++++++\n"

################################################################### MAIN CODE

srcClipDir, srcLabelDir = getArguments()

index_imageList, skipClipList = configReader(os.path.basename(srcClipDir))

#clipPathList = listOfTags(srcClipDir,".png")

