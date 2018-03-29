"""
Renames images and respective labels to start at 1.

EX. if clip11 starts at 145

    clip11/clip11-145.png -> clip11/clip11-1.png
    clip11/clip11-145.txt -> clip11/clip11-1.txt

Usage:
------
	python startFromOne.py -s [<path to /images directory>]
	EX. python startFromOne.py -s /home/ubuntu/annotate_tracking/images
"""

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
	#else:
		#print "> Found directory: " + directoryName 
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

# ---------------------------------------------------------------- list subdirs
def listSubdirs(directoryName):
	print "> Generating list of subdirs for " + directoryName 
	
	nameList = []

	for root, dirs, files in os.walk(directoryName):
		for name in dirs:
			nameList.append(os.path.join(root, name))

	if not nameList:
		print "> List of subdirs is empty!"
		raise SystemExit

	return naturalsort(nameList)

# ---------------------------------------------------------------- find files
def findFiles(directoryName,dotTag):
	#print "> Generating list for " + dotTag + " tags" 
	
	nameList = []

	for root, dirs, files in os.walk(directoryName):
		for name in files:
			if (name.rfind(dotTag) != -1):
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


# ===================================================================
# ===================================================================
class ClipSet:

	def __init__(self, clipDir_path):
		self.imgs_path = clipDir_path
		self.labels_path = clipDir_path.replace("images", "labels")
		self.status = False
		self.clipList = []

	def getClipList(self):
		self.clipList = findFiles(self.imgs_path, ".png")
		#print self.clipList[0]
		#saveListInTxt(self.clipList)

	def checkIfNotOne(self):
		if ((self.clipList[0]).rfind("-1.png") == -1):
			print self.clipList[0] + " is first item"
			self.status = True
		#else:
		#	print "Skipping " + os.path.basename(self.imgs_path)

	def mvFiles(self):
		if self.status:
			counter = 1
			for item in self.clipList:
				cmd = "mv " + item + " " + str(self.imgs_path) + "/" + os.path.basename(self.imgs_path) + "-" + str(counter) + ".png"
				#print cmd
				subprocess.call(cmd, shell=True)


				temp  = item.replace("images", "labels")
				item_label_path = temp.replace(".png", ".txt")
				if(os.path.exists(item_label_path)):
					cmd = "mv " + item_label_path + " " + str(self.labels_path) + "/" + os.path.basename(self.labels_path) + "-" + str(counter) + ".txt"
					#print cmd
					subprocess.call(cmd, shell=True)
				counter += 1

####################################################################################################### GLOBAL VARS
subdirList = []
readContentList = []

####################################################################################################### MAIN CODE
####################################################################################################### MAIN CODE
srcTopDir_images = getArguments()

subdirList = listSubdirs(srcTopDir_images)

#saveListInTxt(subdirList)


for item in subdirList:
	a_clipset = ClipSet(item)
	a_clipset.getClipList()
	a_clipset.checkIfNotOne()
	a_clipset.mvFiles()
	#break


