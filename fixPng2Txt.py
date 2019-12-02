#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
#-------------------------------------------------------------- from rosettacode
from itertools import groupby
from unicodedata import decomposition, name
from pprint import pprint as pp
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

    parser.add_argument('-s', type=str, default=None, dest='srcTop', help='source clip dir path')

    parsedArgs = parser.parse_args()

    if (parsedArgs.srcTop == None):    
        print "> No /images directory path entered!"
        raise SystemExit

    if (parsedArgs.srcTop[-1] == '/'):
        srcTop = parsedArgs.srcTop[0:-1]
    else:
        srcTop = parsedArgs.srcTop

    srcTop = os.path.expanduser(srcTop)
    print "> Verifying source clip directory"
    ifNotDirExit(srcTop)

    return srcTop

# ---------------------------------------------------------------- find files
def findFiles(directoryName,dotTag):
    print "> Generating list for " + dotTag + " tags" 
    
    nameList = []

    for root, dirs, files in os.walk(directoryName):
        for name in files:
            if (name.rfind(dotTag) != -1 and root.rfind("/labels") != -1):
                nameList.append(os.path.join(root, name))

    if not nameList:
        print "> List of tags is empty!"
        raise SystemExit

    return naturalsort(nameList)

# ---------------------------------------------------------------- save list as txt file
def saveListInTxt(givenList):
    savingFile = open("listFiles.txt", "wb")
    for name in givenList:
        savingFile.write("%s\n" % name)
    savingFile.close()

def findDstPath(srcName):
    clusterNum = 0
    while(srcName.rfind("/cluster" + str(clusterNum) + "/") == -1):
        clusterNum += 1
    ifNotDirCreate("./labels/cluster" + str(clusterNum))
    return "./labels/cluster" + str(clusterNum) + "/" + os.path.basename(item)[:-4] + ".txt"

def readContent(txtPath):                                                      
    txtFile = open(txtPath,"r")
    contentList = []
    for content in iter(txtFile):
        #print content
        content1 = content.replace('\'','')
        content2 = content1.replace('[','')
        content3 = content2.replace(']','')
        contentF = content3.replace(',','')
        #print contentF
        contentList.append(contentF)


    txtFile.close()
    return contentList

def saveFixLabel(dstPath,contentList):
    savingFile = open(dstPath, "wb")
    for content in contentList:
        savingFile.write("%s" % content)
    savingFile.close()

####################################################################################################### GLOBAL VARS
problemList = []
readContentList = []

####################################################################################################### MAIN CODE
####################################################################################################### MAIN CODE
srcTopDir = getArguments()

problemList = findFiles(srcTopDir, ".png")

#saveListInTxt(problemList)
ifNotDirCreate("./labels")
for item in problemList:
    #print item
    dstPath = findDstPath(item)
    readContentList = readContent(item)
    saveFixLabel(dstPath,readContentList)
    #break