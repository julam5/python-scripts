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
    parser.add_argument('-d', type=str, default="./", dest='dstTop', help='destination top dir path')
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
# ---------------------------------------------------------------- find files
def findDirs(directoryName,dotTag):
	print "> Generating list for " + dotTag + " tags" 

	dirList = []

	for root, dirs, files in os.walk(directoryName):
		for name in dirs:
			if (name.rfind(dotTag) != -1 and os.path.join(root, name).rfind("/images") != -1):
				print os.path.join(root, name)
				dirList.append(os.path.join(root, name))

	if not dirList:
		print "> Did not find any */cluster* dirs! Exiting"
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

    #if not fileList:
    #    print "> fileList is empty! Exiting"
    #    raise SystemExit

    return fileList
    #return naturalsort(fileList)

# ---------------------------------------------------------------- save list as txt file
def saveListInTxt(givenList):
    savingFile = open("imgList.txt", "wb")
    for name in givenList:
        savingFile.write("%s\n" % name)
    savingFile.close()

def createSymlinkInDir(directoryName,path,link):
	clusterDir = "/" + os.path.basename(os.path.dirname(path))
	dstImgPath = directoryName + "/images" + clusterDir + clusterDir + "_" + os.path.basename(path)

	ifNotDirCreate(directoryName)
	ifNotDirCreate(directoryName + "/images")
	ifNotDirCreate(directoryName + "/labels")
	ifNotDirCreate(directoryName + "/images" + clusterDir)
	ifNotDirCreate(directoryName + "/labels" + clusterDir)

	if(link):
		os.symlink(path,dstImgPath)
	else:
		subprocess.call("cp " + path + " " + dstImgPath, shell=True)

	replace1 = path.replace("/images", "/labels")
	labelPath = replace1.replace("png","txt")
	labelPath = labelPath.replace("jpg","txt")
	labelPath = labelPath.replace("JPG","txt")
	labelPath = labelPath.replace("jpeg","txt")
	dstLabPath = directoryName + "/labels" + "/" + clusterDir + clusterDir + "_" + os.path.basename(labelPath)

	if os.path.isfile(labelPath):
		if(link):
			os.symlink(labelPath,dstLabPath)
		else:
			subprocess.call("cp " + labelPath + " " + dstLabPath, shell=True)

####################################################################################################### GLOBAL VARS
clusterList = []
imageList = []
counter = 0
percent60 = 0
percent20 = 0
####################################################################################################### MAIN CODE
####################################################################################################### MAIN CODE

topSrcPath, topDstPath, link = readArguments()

clusterList = findDirs(topSrcPath, "cluster")

#print clusterList
#for cluster in clusterList:
#	pngList = findFiles(cluster, ".png")
#	jpgList = findFiles(cluster, ".jpg")
#	JPGList = findFiles(cluster, ".JPG")
#	jpegList = findFiles(cluster, ".jpeg")


