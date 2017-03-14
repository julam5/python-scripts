#!/usr/bin/env python

import subprocess
import sys
import os
import argparse

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

	if (srcLabelDir == ''):    
		srcLabelDir = raw_input("> Enter source label folder path (use . and .. if necessary): ")

	srcLabelDir = os.path.expanduser(srcLabelDir)

	return srcClipDir, srcLabelDir

################################################################### MAIN CODE

srcClipDir, srcLabelDir = getArguments()

print srcClipDir
print srcLabelDir