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


#ANGLE FOR ROTATION=========================================================
alpha = 90 #goes CCW

def writeAngle():
    print('creating new text file with input angle ' + str(alpha))
    alphaFile = open('rotationAngle', 'w')
    alphaFile.write(str(alpha))
writeAngle()

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

#code for rotating image======================================================
#taken from stack overflow:
#http://stackoverflow.com/questions/16702966/rotate-image-and-crop-out-black-borders
def getTranslationMatrix2d(dx, dy):
##    """
##    Returns a numpy affine transformation matrix for a 2D translation of
##    (dx, dy)
##    """
    return np.matrix([[1, 0, dx], [0, 1, dy], [0, 0, 1]])


def rotateImage(image, angle):
##    """
##    Rotates the given image about it's centre
##    """

    image_size = (image.shape[1], image.shape[0])
    image_center = tuple(np.array(image_size) / 2)

    rot_mat = np.vstack([cv2.getRotationMatrix2D(image_center, angle, 1.0), [0, 0, 1]])
    trans_mat = np.identity(3)

    w2 = image_size[0] * 0.5
    h2 = image_size[1] * 0.5

    rot_mat_notranslate = np.matrix(rot_mat[0:2, 0:2])

    tl = (np.array([-w2, h2]) * rot_mat_notranslate).A[0]
    tr = (np.array([w2, h2]) * rot_mat_notranslate).A[0]
    bl = (np.array([-w2, -h2]) * rot_mat_notranslate).A[0]
    br = (np.array([w2, -h2]) * rot_mat_notranslate).A[0]

    x_coords = [pt[0] for pt in [tl, tr, bl, br]]
    x_pos = [x for x in x_coords if x > 0]
    x_neg = [x for x in x_coords if x < 0]

    y_coords = [pt[1] for pt in [tl, tr, bl, br]]
    y_pos = [y for y in y_coords if y > 0]
    y_neg = [y for y in y_coords if y < 0]

    right_bound = max(x_pos)
    left_bound = min(x_neg)
    top_bound = max(y_pos)
    bot_bound = min(y_neg)

    new_w = int(abs(right_bound - left_bound))
    new_h = int(abs(top_bound - bot_bound))
    new_image_size = (new_w, new_h)

    new_midx = new_w * 0.5
    new_midy = new_h * 0.5

    dx = int(new_midx - w2)
    dy = int(new_midy - h2)

    trans_mat = getTranslationMatrix2d(dx, dy)
    affine_mat = (np.matrix(trans_mat) * np.matrix(rot_mat))[0:2, :]
    result = cv2.warpAffine(image, affine_mat, new_image_size, flags=cv2.INTER_LINEAR)

    return result


#==============================================================================
def generate_clipfile(clipDirName):
    print "> Generating img list"

    tag1=".png" #
    nameList = []

    for root, dirs, files in os.walk(clipDirName, topdown=False):
        for name in files:
            if (name.rfind(tag1) != -1 ):
                nameList.append(os.path.join(root, name))          

    return naturalsort(nameList)

# #####################################################################################################################   MAIN CODE START
# ============================================================================= Global Vars
clipNames = []
dstDir = ""
dstFile = ""
clipGroup = ""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ---------------------------------------------------------------------------- Check for config file (checked)
parser = argparse.ArgumentParser(description='Img editor')
parser.add_argument('-s', type=str, default=''  , dest='clipSource' , help='top parent source directory name with png images')
parsedArgs = parser.parse_args()

if (len(parsedArgs.clipSource) != 0 and parsedArgs.clipSource[len(parsedArgs.clipSource)-1] == '/'):
    clipSource = parsedArgs.clipSource[0:-1]
else:
    clipSource = parsedArgs.clipSource
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ---------------------------------------------------------------------------- if config file will NOT be used (checked)
if (clipSource == ''):    
    clipSource = raw_input("> Enter clip directory's path (use . and .. if necessary): ")

# --------------------------------------------------------------------------- check if image directory exists (checked)
if (os.path.isdir(clipSource) is False): 
    print "> " + clipSource + " is not a valid path!"
    raise SystemExit

clipNames = generate_clipfile(clipSource)

# --------------------------------------------------------------------------- if clipNames is empty, exit (checked)
if not clipNames:
    print "> Clip list is empty!"
    raise SystemExit


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

for clip in clipNames:
    clipGroup = clip[clip.rfind("/"):clip.rfind("-")]
    
    dstDir = "./images_GD_90" + clipGroup + "_GD_" + str(alpha) #os.path.dirname(clip)
    if (os.path.isdir(dstDir) is False): 
        print "> " + dstDir + " doesn't exist in current directory!\nCreating " + dstDir + " directory"
        os.makedirs(dstDir)
    dstFile = dstDir + clip[clip.rfind("/"):clip.rfind(".")] + ".png"
    #print dstFile

    img = cv2.imread(clip, -1)
    dst = rotateImage(img, alpha)
    cv2.imwrite(dstFile, dst)


