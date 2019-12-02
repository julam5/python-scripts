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

# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- parse arguments passed
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='~', dest='clipSource', help='top parent source directory name with videos (Default is ~/Downloads)')
parser.add_argument('-n', type=int, default=1, dest='clipnum', help='starting clip number')
parser.add_argument('-f', type=int, default=1, dest='fps', help='fps for rec')

parsedArgs = parser.parse_args()

if (len(parsedArgs.clipSource) != 0 and parsedArgs.clipSource[len(parsedArgs.clipSource)-1] == '/'):
    clipSource = parsedArgs.clipSource[0:-1]
else:
    clipSource = parsedArgs.clipSource


print "\n> Using " + clipSource + " as video source directory"
print "> Starting @ clip number " + str((parsedArgs.clipnum))

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

# ---------------------------------------------------------------- create img object and add it to imgList with name set
if (os.path.isdir("./Clips") is False):
    os.mkdir( "./Clips")
    print "> Created ./Clips directory!"

############################################################################################################################################################

for clip in videoList:
    if (os.path.isdir("./Clips/clip" + str(parsedArgs.clipnum)) is False):
        print "> " + "./Clips/clip" + str(parsedArgs.clipnum) + " doesn't exist in current directory! Creating " + "./Clips/clip" + str(parsedArgs.clipnum) + " directory"
        os.makedirs("./Clips/clip" + str(parsedArgs.clipnum))

#jpg -qscale:v 1
    #print "ffmpeg -i " + clip + " -qscale:v 2 -vf fps=10 ./Clips/clip" + str(parsedArgs.clipnum) + "/clip" + str(parsedArgs.clipnum) + "-%d.jpg"
    subprocess.call("ffmpeg -i " + clip + " -c:v png -vf fps=" + str(parsedArgs.fps) + " ./Clips/clip" + str(parsedArgs.clipnum) + "/clip" + str(parsedArgs.clipnum) + "-%d.png", shell=True)
    parsedArgs.clipnum += 1

# increasing fps makes more pics appear















