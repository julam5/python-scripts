#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
#-------------------------------------------------------------- from rosettacode
from itertools import groupby
from unicodedata import decomposition, name
from pprint import pprint as pp
# ================================================================================ Natural sorting 
#-------------------------------------------------------------- from rosettacode
commonleaders = ['the'] # lowercase leading words to ignore
 
hexdigits = set('0123456789abcdef')
decdigits = set('0123456789')   # Don't use str.isnumeric
 
def splitchar(c):
    ' De-ligature. De-accent a char'
    de = decomposition(c)
    if de:
        # Just the words that are also hex numbers
        de = [d for d in de.split()
                  if all(c.lower()
                         in hexdigits for c in d)]
        n = name(c, c).upper()
        # (Gosh it's onerous)
        if 'LIGATURE' in n:
            # Assume two character ligature
            base += others.pop(0)
    else:
        base = c
    return base
 
 
def sortkeygen(s):
    # Ignore leading and trailing spaces
    s = unicode(s).strip()
    # All space types are equivalent
    s = ' '.join(s.split())
    # case insentsitive
    s = s.lower()
    # Title
    words = s.split()
    if len(words) > 1 and words[0] in commonleaders:
        s = ' '.join( words[1:])
    # accent and ligatures
    s = ''.join(splitchar(c) for c in s)
    # Numeric sections as numerics
    s = [ int("".join(g)) if isinteger else "".join(g)
          for isinteger,g in groupby(s, lambda x: x in decdigits)]
 
    return s
 
def naturalsort(items):
    return sorted(items, key=sortkeygen)
# ================================================================================ Natural sorting 

# ================================================================================ Generate clipFile.txt
# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- parse arguments passed
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='~', dest='clipSource', help='top parent source directory name with videos (Default is ~/Downloads)')

parsedArgs = parser.parse_args()

if (len(parsedArgs.clipSource) != 0 and parsedArgs.clipSource[len(parsedArgs.clipSource)-1] == '/'):
    clipSource = parsedArgs.clipSource[0:-1]
else:
    clipSource = parsedArgs.clipSource


print "\n> Using " + clipSource + " as video source directory"

tag1=".mp4"
tag2=".mov"
nameList = []
videoList = []

# ---------------------------------------------------------------- generate clipFile.txt if images file exists
if (os.path.isdir(parsedArgs.clipSource) is False): 
    print "> "+ clipSource + " was not found!"
    raise SystemExit

for root, dirs, files in os.walk(clipSource, topdown=False):
    for name in files:
        name1 = name.lower()
        if name1.rfind(tag1) != -1 or name1.rfind(tag2) != -1:
            nameList.append(os.path.join(root, name))          

videoList = naturalsort(nameList)
#################################################### convert video into 720p video and place into ./720_videos

if (os.path.isdir("720_videos") is False):
    os.mkdir( "./720_videos")
    print "> Created 720_videos directory!"

clipList = []
for video in videoList:
    videoDest = "./720_videos/clip_720_" + os.path.basename(video)

    #print "ffmpeg -i " + video + " -qscale:v 2 -vf scale=1280:720 " + videoDest + " -hide_banner"
    subprocess.call("ffmpeg -i " + video + " -vf scale=1280:720 " + videoDest, shell=True)















