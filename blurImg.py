#!/usr/bin/env python

import ConfigParser
import os
import cv2
import numpy as np
import argparse
import ast
import copy

#takes images from folder directory and then runs a blur function,
#once altered, takes images and stores into new folder


#double loop
#first loop starts at first clip folder and checks if it exists

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

#============================================================================
def generate_clipfile(clipDirName):
    print "> Generating img list"

    tag1=".png" #
    nameList = []

    for root, dirs, files in os.walk(clipDirName, topdown=False):
        for name in files:
            if (name.rfind(tag1) != -1 ):
                nameList.append(os.path.join(root, name))          

    return naturalsort(nameList)


#============================================================================
# #####################################################################################################################   MAIN CODE START
# =============================================================================================================== Global Vars
clipNames = []
dstDir = ""
dstFile = ""
clipGroup = ""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- Check for config file (checked)
parser = argparse.ArgumentParser(description='Img editor')
parser.add_argument('-s', type=str, default=''  , dest='clipSource' , help='top parent source directory name with png images')
parsedArgs = parser.parse_args()

if (len(parsedArgs.clipSource) != 0 and parsedArgs.clipSource[len(parsedArgs.clipSource)-1] == '/'):
    clipSource = parsedArgs.clipSource[0:-1]
else:
    clipSource = parsedArgs.clipSource
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# --------------------------------------------------------------------------------------------------------------- if config file will NOT be used (checked)
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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

for clip in clipNames:
    clipGroup = clip[clip.rfind("/"):clip.rfind("-")]
    dstDir = "./images_OD_blur" + clipGroup + "_OD_blur" #os.path.dirname(clip)
    if (os.path.isdir(dstDir) is False): 
        print "> " + dstDir + " doesn't exist in current directory!\nCreating " + dstDir + " directory"
        os.makedirs(dstDir)
    dstFile = dstDir + clip[clip.rfind("/"):clip.rfind(".")] + ".png"
    #print dstFile

    img = cv2.imread(clip, -1)
    blur = cv2.blur(img,(20,20))
    cv2.imwrite(dstFile, blur)


