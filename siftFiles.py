#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
#-------------------------------------------------------------- from rosettacode
from itertools import groupby
from unicodedata import decomposition, name
from pprint import pprint as pp
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

# ---------------------------------------------------------------- parse arguments passed
def getArguments():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-c', type=str, default='', dest='srcClipDir', help='source clip dir path')
    parser.add_argument('-l', type=str, default='', dest='srcLabelDir', help='source label dir path')

    parsedArgs = parser.parse_args()

    if (len(parsedArgs.srcClipDir) != 0 and parsedArgs.srcClipDir[len(parsedArgs.srcClipDir)-1] == '/'):
        srcClipDir = parsedArgs.srcClipDir[0:-1]
    else:
        srcClipDir = parsedArgs.srcClipDir

    if (srcClipDir == ''):    
        srcClipDir = raw_input("> Enter source clip folder path (use . and .. if necessary): ")

    srcClipDir = os.path.expanduser(srcClipDir)

    if (len(parsedArgs.srcLabelDir) != 0 and parsedArgs.srcLabelDir[len(parsedArgs.srcLabelDir)-1] == '/'):
        srcLabelDir = parsedArgs.srcLabelDir[0:-1]
    else:
        srcLabelDir = parsedArgs.srcLabelDir

    #if (srcLabelDir == ''):    
    #    srcLabelDir = raw_input("> Enter source label folder path (use . and .. if necessary): ")

    #srcLabelDir = os.path.expanduser(srcLabelDir)

    return srcClipDir, srcLabelDir

# ---------------------------------------------------------------- generated files
def listOfTags(dirName):
    print "> Generating list of tags" 
    
    nameList = []

    for root, dirs, files in os.walk(dirName):
        for name in files:
            if (name[-4:] != ".jpg" and name[-4:] != ".png" and name[-4:] != ".JPG" and name[-5:] != ".jpeg" and name[-3:] != ".py" and name[-4:] != ".txt"):
                nameList.append(os.path.join(root, name))          

    return naturalsort(nameList)

def saveList(clipNames):
    savingFile = open("addrsOfTags.txt", "wb")
    for name in clipNames:
        savingFile.write("%s\n" % name)
    savingFile.close()
################################################################### MAIN CODE

srcClipDir, srcLabelDir = getArguments()

clipList = []

clipList = listOfTags(srcClipDir)
#saveList(clipList)
for clip in clipList:
    #print "rm " + clip
    subprocess.call("rm " + clip, shell=True)















