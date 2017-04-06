#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
import random

# ---------------------------------------------------------------- parse arguments passed
def readArguments():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-s', type=str, default=None, dest='srcTop', help='source top dir path')
    parser.add_argument('-d', type=str, default=None, dest='dstTop', help='destination top dir path')
    parser.add_argument('-l', type=int, default=1, dest='link', help='enter integer to create (0=copies) or (1=links) of images and labels')  

    parsedArgs = parser.parse_args()

    if (parsedArgs.srcTop == None):    
        print "> No source directory path entered!"
        raise SystemExit

    if (parsedArgs.srcTop[-1] == '/'):
        srcTop = parsedArgs.srcTop[0:-1]
    else:
        srcTop = parsedArgs.srcTop

    srcTop = os.path.expanduser(srcTop)
    print "> Verifying source clip directory"
    ifNotDirExit(srcTop)

    if (parsedArgs.dstTop == None):    
        print "> No destination directory path entered!"
        raise SystemExit

    if (parsedArgs.dstTop[-1] == '/'):
        dstTop = parsedArgs.dstTop[0:-1]
    else:
        dstTop = parsedArgs.dstTop
    dstTop = os.path.expanduser(dstTop)
    print "> Verifying destination clip directory"
    ifNotDirExit(dstTop)

    if parsedArgs.link > 1:
    	link = 1
    else:
    	link = parsedArgs.link

    return srcTop,dstTop,link

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


# ---------------------------------------------------------------- determine mode
def modeSelection(directoryName):
	if (os.path.isdir(directoryName + "/images") and os.path.isdir(directoryName + "/labels")):
		return 0
	else:
		return 1

# ---------------------------------------------------------------- find directories
def findDirsInTopSrc(directoryName):
	print "> Generating list of dirs"

	dirList = []

	for root, dirs, files in os.walk(directoryName):
		for name in dirs:
			if (os.path.dirname(os.path.join(root, name)) == directoryName):
				dirList.append(os.path.join(root, name))

	if not dirList:
		print "> Did not find any */images/cluster* dirs! Exiting"
		raise SystemExit

	return dirList
	#return naturalsort(fileList)

# ---------------------------------------------------------------- find files
def findFiles(directoryName,dotTag):
    print "> Generating list for " + dotTag + " tags" 
    
    fileList = []

    for root, dirs, files in os.walk(directoryName):
        for name in files:
            if (name.rfind(dotTag) != -1):
                fileList.append(os.path.join(root, name))

    return fileList

# ---------------------------------------------------------------- save list as txt file
def saveListInTxt(givenList):
    savingFile = open("dirList.txt", "wb")
    for name in givenList:
        savingFile.write("%s\n" % name)
    savingFile.close()

def createSymlinkInDir(dstDirName,srcImgPath,link,srcDirPath, mode):
	withoutSrcPathImg = srcImgPath.replace(srcDirPath,"")
	dstImgPath = dstDirName + withoutSrcPathImg
	#print dstImgPath

	ifNotDirCreate(os.path.dirname(dstImgPath))

	if(link):
		os.symlink(path,dstImgPath)
	else:
		subprocess.call("cp " + path + " " + dstImgPath, shell=True)

	if not mode:
		srcLabelPath = srcImgPath.replace("/images", "/labels")
		srcLabelPath = srcLabelPath.replace("png","txt")
		srcLabelPath = srcLabelPath.replace("jpg","txt")
		srcLabelPath = srcLabelPath.replace("JPG","txt")
		srcLabelPath = srcLabelPath.replace("jpeg","txt")

		withoutSrcPathLabel = srcLabelPath.replace(srcDirPath,"")

		if os.path.isfile(srcLabelPath):
			dstLabPath = dstDirName + withoutSrcPathLabel
			ifNotDirCreate(os.path.dirname(dstLabPath))
			if(link):
				os.symlink(srcLabelPath,dstLabPath)
			else:
				subprocess.call("cp " + srcLabelPath + " " + dstLabPath, shell=True)

####################################################################################################### GLOBAL VARS
topSrcDirList = []
imageList = []
counter = 0
percent60 = 0
percent20 = 0
mode = 0
####################################################################################################### MAIN CODE
####################################################################################################### MAIN CODE

topSrcPath, topDstPath, link = readArguments()

mode = modeSelection(topSrcPath) #0 = images/labels struct; 1=images struct

#determine list of dirs with 60-20-20
if mode:
	topSrcDirList = findDirsInTopSrc(topSrcPath)
else: 
	topSrcDirList = findDirsInTopSrc(topSrcPath + "/images")

saveListInTxt(topSrcDirList)

for aDir in topSrcDirList:
	print "\n> Current Directory: " + aDir
	pngList = findFiles(aDir, ".png")
	jpgList = findFiles(aDir, ".jpg")
	JPGList = findFiles(aDir, ".JPG")
	jpegList = findFiles(aDir, ".jpeg")

	imageList = pngList + jpgList + JPGList + jpegList

	if not imageList:
		print "> " + aDir +" has no images! Moving on!"
		continue

	random.shuffle(imageList)

	saveListInTxt(imageList)

	#print len(imageList)
	percent60 = int(round(len(imageList) * 0.6))
	percent20 = int(round(len(imageList) * 0.2))
	#print percent60
	#print percent20

	for path in imageList:
		if counter < percent60:
			createSymlinkInDir(topDstPath + "/training",path,link,topSrcPath, mode)
		elif counter < (percent60+percent20):
			createSymlinkInDir(topDstPath + "/testing",path,link,topSrcPath, mode)
		else:
			createSymlinkInDir(topDstPath + "/validation",path,link,topSrcPath, mode)
		counter += 1
	counter = 0
	del imageList

