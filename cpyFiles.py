#!/usr/bin/env python

import subprocess
import sys
import os
import argparse

# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- parse arguments passed
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='', dest='clipSource', help='orig text file')
parser.add_argument('-b', type=int, default=1, dest='beginNum', help='starting text file number')
parser.add_argument('-e', type=int, default=1, dest='endNum', help='starting text file number')

parsedArgs = parser.parse_args()

print "\n> Using " +parsedArgs.clipSource+ " as text source"

# ---------------------------------------------------------------
indexRfind = parsedArgs.clipSource.rfind("-")
textDirname = parsedArgs.clipSource[0:indexRfind+1]

for num in range(parsedArgs.beginNum, parsedArgs.endNum+1):
    #print "cp " + parsedArgs.clipSource + " " + textDirname + str(num) + ".txt"
    subprocess.call("cp " + parsedArgs.clipSource + " " + textDirname + str(num) + ".txt", shell=True)
  














