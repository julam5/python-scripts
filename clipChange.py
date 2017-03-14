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
def generate_clipfile(clipFileName):
    print "\n> Updating clipFiles.txt"

    tag1=".jpg"

    clipFile = open("./clipFiles.txt", "wb")

    nameList = []

    for root, dirs, files in os.walk(clipFileName, topdown=False):
        for name in files:
            name1 = name.lower()
            if (name1.rfind(tag1) != -1): # seek at videos but not those already converted by this program
                nameList.append(os.path.join(root,name))          

    nameList2 = naturalsort(nameList)

    for item in nameList2:
        clipFile.write("%s\n" % item)

    clipFile.close()
    print "> Done generating clipFiles.txt!\n"
# ================================================================================ Generate clipFile.txt
# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# ##############################################################################################################################################################################
# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- parse arguments passed
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='~/Downloads', dest='clipSource', help='top parent source directory name with videos (Default is ~/Downloads)')
parser.add_argument('-n', type=int, default=1, dest='clipnum', help='starting clip number')

parsedArgs = parser.parse_args()

print "\n> Using " +parsedArgs.clipSource+ " as video source directory"
print "> Starting @ clip number " + str((parsedArgs.clipnum))

# ---------------------------------------------------------------- generate clipFile.txt if images file exists
if (os.path.isdir(parsedArgs.clipSource) is False): 
    print "> "+parsedArgs.clipSource + " doesn't exist in current directory! either create or move this program to where " + parsedArgs.clipSource + " is"
    raise SystemExit

generate_clipfile(parsedArgs.clipSource)

# ---------------------------------------------------------------- if clipFile.txt is empty, exit
if (os.stat("./clipFiles.txt").st_size == 0):
    print "> clipFiles.txt is empty!"
    raise SystemExit

# ---------------------------------------------------------------- create img object and add it to imgList with name set
clipList = []
clipFile = open("./clipFiles.txt", "r")

for line in iter(clipFile):
    lineN = line.rstrip('\n')
    clipList.append(lineN)

clipFile.close()

############################################################################################################################################################
############################################################################################################################################################

if (os.path.isdir("./clip" + str(parsedArgs.clipnum)) is False):
    os.mkdir( "./clip" + str(parsedArgs.clipnum))
    print "> Created " + "./clip" + str(parsedArgs.clipnum) + " directory!"

num = 1
for clip in clipList:
    #print "mv " + clip + " " + "./clip" + str(parsedArgs.clipnum) + "/clip" + str(parsedArgs.clipnum) + "-" + str(num) + ".jpg"
    
    subprocess.call("mv " + clip + " " + "./clip" + str(parsedArgs.clipnum) + "/clip" + str(parsedArgs.clipnum) + "-" + str(num) + ".jpg", shell=True)
    num += 1














