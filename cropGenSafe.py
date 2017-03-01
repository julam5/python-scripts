#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
import csv
import numpy as np
# #######################################################################################   Fxns

# #######################################################################################   Global Vars
sourceAddr = "/home/justin/"
topDirName = "./yolo"


# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- take in arguments
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='', dest='csvSource', help='orig text file')
parser.add_argument('-n', type=int, default=0, dest='numClusters', help='number of clusters')

parsedArgs = parser.parse_args()

# ---------------------------------------------------- check csvSource
if (len(parsedArgs.csvSource) == 0 or not os.path.isfile(parsedArgs.csvSource)):
    print "> csv source is invalid!"
    raise SystemExit
else:
    addrCsvSource = parsedArgs.csvSource

print "\n> Using " + addrCsvSource + " as text source"

# ---------------------------------------------------- check number of clusters
if (parsedArgs.numClusters == 0):
    numClusters = int(raw_input("==> Enter number of clusters: "))
else:
    numClusters = parsedArgs.numClusters

print "\n> Number of clusters is " + str(numClusters)

# ---------------------------------------------------------------- create top dir and subdirs in current dir of script
# ---------------------------------------------------- create top directory if needed
if (os.path.isdir(topDirName) is False):
    print "> " + topDirName + " doesn't exist! Creating " + topDirName
    os.makedirs(topDirName)

    for numCount in range(0,numClusters):
    	#print topDirName + "/" + "cluster" + str(numCount)
    	#print topDirName + "/" + "cluster" + str(numCount) + "/images"
    	#print topDirName + "/" + "cluster" + str(numCount) + "/labels"

    	os.makedirs(topDirName + "/" + "cluster" + str(numCount))
    	os.makedirs(topDirName + "/" + "cluster" + str(numCount) + "/images")
    	os.makedirs(topDirName + "/" + "cluster" + str(numCount) + "/labels")


# ----------------------------------------------------
with open(addrCsvSource, 'rb') as f:
    reader = csv.reader(f)
    for line in reader:
        print sourceAddr + line[0] + " " + line[1]
        break





