#!/usr/bin/env python

"""
Reads all images in input /images directory and augments each .png or .jpg into an output directory called "./aug_images/"

Usage:
------
	python imgaugTest.py -s [<path to /images>]
"""

from __future__ import print_function, division
import imgaug as ia
from imgaug import augmenters as iaa
from imgaug import parameters as iap
import numpy as np
from scipy import ndimage, misc
from skimage import data
import matplotlib.pyplot as plt
from matplotlib import gridspec
import six
import six.moves as sm

import subprocess
import sys
import os
import argparse
#-------------------------------------------------------------- from rosettacode
from itertools import groupby
from unicodedata import decomposition, name
from pprint import pprint as pp

####################################################################################################### GLOBAL VARS

np.random.seed(44)
ia.seed(44)

commonleaders = ['the'] # lowercase leading words to ignore
 
hexdigits = set('0123456789abcdef')
decdigits = set('0123456789')   # Don't use str.isnumeric

outputDir = "./aug_images/"

fileList = []
readContentList = []

####################################################################################################### MAIN CODE
####################################################################################################### MAIN CODE

def main():
	srcTopDir = getArguments()
	fileList = findImgFiles(srcTopDir)
	#saveListInTxt(fileList)
	
	ifNotDirCreate(outputDir)

	for image in fileList:
		draw_per_augmenter_images(image)

####################################################################################################### FUNCTIONS
# ====================================================================================================== Natural sorting from rosettacode
 
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
		print ("> " + directoryName + " is not a valid directory! Exiting.")
		raise SystemExit
	else:
		print ("> Found directory: " + directoryName) 
# ---------------------------------------------------------------- check if path is directory, if not exit program
def ifNotDirCreate(directoryName):
	if (os.path.isdir(directoryName) is False): 
		print ("> " + directoryName + " is not a valid directory! Creating it.")
		os.makedirs(directoryName)
	#else:
		#print "> Found directory: " + directoryName 
# ---------------------------------------------------------------- parse arguments passed
def getArguments():
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-s', type=str, default=None, dest='srcTop', help='source clip dir path')

	parsedArgs = parser.parse_args()

	if (parsedArgs.srcTop == None):    
		print ("> No /images directory path entered!")
		raise SystemExit

	if (parsedArgs.srcTop[-1] == '/'):
		srcTop = parsedArgs.srcTop[0:-1]
	else:
		srcTop = parsedArgs.srcTop

	srcTop = os.path.expanduser(srcTop)
	print ("> Verifying source clip directory")
	ifNotDirExit(srcTop)

	return srcTop

# ---------------------------------------------------------------- find files
def findImgFiles(directoryName):
	print ("> Generating filenames list") 
	
	nameList = []

	for root, dirs, files in os.walk(directoryName):
		for name in files:
			if (name.rfind(".png") != -1 or \
				name.rfind(".jpg") != -1 or \
				name.rfind(".JPEG") != -1 or \
				name.rfind(".jpeg") != -1):
				nameList.append(os.path.join(root, name))

	if not nameList:
		print ("> List of tags is empty!")
		raise SystemExit

	return naturalsort(nameList)

# ---------------------------------------------------------------- save list as txt file
def saveListInTxt(givenList):
	savingFile = open("listFiles.txt", "wb")
	for name in givenList:
		savingFile.write("%s\n" % name)
	savingFile.close()

def draw_per_augmenter_images(imgName):
    print("[draw_per_augmenter_images] Loading image...")
    image = misc.imresize(ndimage.imread(imgName), (227, 227))

    #keypoints = [ia.Keypoint(x=43, y=43), ia.Keypoint(x=78, y=40), ia.Keypoint(x=64, y=73)] # left eye, right eye, mouth
    #keypoints = [ia.Keypoint(x=34, y=15), ia.Keypoint(x=85, y=13), ia.Keypoint(x=63, y=73)] # left ear, right ear, mouth
    #keypoints = [ia.KeypointsOnImage(keypoints, shape=image.shape)]

    print("[draw_per_augmenter_images] Initializing...")
    rows_augmenters = [
        #("Noop", [("", iaa.Noop()) for _ in sm.xrange(5)]),
        #("Crop", [iaa.Crop(px=vals) for vals in [(2, 4), (4, 8), (6, 16), (8, 32), (10, 64)]]),
        ("Crop\n(top, right,\nbottom, left)", [(str(vals), iaa.Crop(px=vals)) for vals in [(2, 0, 0, 0), (0, 8, 8, 0), (4, 0, 16, 4), (8, 0, 0, 32), (32, 64, 0, 0)]]),
        ("Fliplr", [(str(p), iaa.Fliplr(p)) for p in [0, 0, 1, 1, 1]]),
        ("Flipud", [(str(p), iaa.Flipud(p)) for p in [0, 0, 1, 1, 1]]),
        ("Superpixels\np_replace=1", [("n_segments=%d" % (n_segments,), iaa.Superpixels(p_replace=1.0, n_segments=n_segments)) for n_segments in [25, 50, 75, 100, 125]]),
        ("Superpixels\nn_segments=100", [("p_replace=%.2f" % (p_replace,), iaa.Superpixels(p_replace=p_replace, n_segments=100)) for p_replace in [0, 0.25, 0.5, 0.75, 1.0]]),
        ("Invert", [("p=%d" % (p,), iaa.Invert(p=p)) for p in [0, 0, 1, 1, 1]]),
        ("Invert\n(per_channel)", [("p=%.2f" % (p,), iaa.Invert(p=p, per_channel=True)) for p in [0.5, 0.5, 0.5, 0.5, 0.5]]),
        ("Add", [("value=%d" % (val,), iaa.Add(val)) for val in [-45, -25, 0, 25, 45]]),
        ("Add\n(per channel)", [("value=(%d, %d)" % (vals[0], vals[1],), iaa.Add(vals, per_channel=True)) for vals in [(-55, -35), (-35, -15), (-10, 10), (15, 35), (35, 55)]]),
        ("Multiply", [("value=%.2f" % (val,), iaa.Multiply(val)) for val in [0.25, 0.5, 1.0, 1.25, 1.5]]),
        ("Multiply\n(per channel)", [("value=(%.2f, %.2f)" % (vals[0], vals[1],), iaa.Multiply(vals, per_channel=True)) for vals in [(0.15, 0.35), (0.4, 0.6), (0.9, 1.1), (1.15, 1.35), (1.4, 1.6)]]),
        ("GaussianBlur", [("sigma=%.2f" % (sigma,), iaa.GaussianBlur(sigma=sigma)) for sigma in [0.25, 0.50, 1.0, 2.0, 4.0]]),
        ("AverageBlur", [("k=%d" % (k,), iaa.AverageBlur(k=k)) for k in [1, 3, 5, 7, 9]]),
        ("MedianBlur", [("k=%d" % (k,), iaa.MedianBlur(k=k)) for k in [1, 3, 5, 7, 9]]),
        ("Sharpen\n(alpha=1)", [("lightness=%.2f" % (lightness,), iaa.Sharpen(alpha=1, lightness=lightness)) for lightness in [0, 0.5, 1.0, 1.5, 2.0]]),
        ("Emboss\n(alpha=1)", [("strength=%.2f" % (strength,), iaa.Emboss(alpha=1, strength=strength)) for strength in [0, 0.5, 1.0, 1.5, 2.0]]),
        ("EdgeDetect", [("alpha=%.2f" % (alpha,), iaa.EdgeDetect(alpha=alpha)) for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]]),
        ("DirectedEdgeDetect\n(alpha=1)", [("direction=%.2f" % (direction,), iaa.DirectedEdgeDetect(alpha=1, direction=direction)) for direction in [0.0, 1*(360/5)/360, 2*(360/5)/360, 3*(360/5)/360, 4*(360/5)/360]]),
        ("AdditiveGaussianNoise", [("scale=%.2f*255" % (scale,), iaa.AdditiveGaussianNoise(scale=scale * 255)) for scale in [0.025, 0.05, 0.1, 0.2, 0.3]]),
        ("AdditiveGaussianNoise\n(per channel)", [("scale=%.2f*255" % (scale,), iaa.AdditiveGaussianNoise(scale=scale * 255, per_channel=True)) for scale in [0.025, 0.05, 0.1, 0.2, 0.3]]),
        ("Dropout", [("p=%.2f" % (p,), iaa.Dropout(p=p)) for p in [0.025, 0.05, 0.1, 0.2, 0.4]]),
        ("Dropout\n(per channel)", [("p=%.2f" % (p,), iaa.Dropout(p=p, per_channel=True)) for p in [0.025, 0.05, 0.1, 0.2, 0.4]]),
        ("CoarseDropout\n(p=0.2)", [("size_percent=%.2f" % (size_percent,), iaa.CoarseDropout(p=0.2, size_percent=size_percent, min_size=2)) for size_percent in [0.3, 0.2, 0.1, 0.05, 0.02]]),
        ("CoarseDropout\n(p=0.2, per channel)", [("size_percent=%.2f" % (size_percent,), iaa.CoarseDropout(p=0.2, size_percent=size_percent, per_channel=True, min_size=2)) for size_percent in [0.3, 0.2, 0.1, 0.05, 0.02]]),
        ("ContrastNormalization", [("alpha=%.1f" % (alpha,), iaa.ContrastNormalization(alpha=alpha)) for alpha in [0.5, 0.75, 1.0, 1.25, 1.50]]),
        ("ContrastNormalization\n(per channel)", [("alpha=(%.2f, %.2f)" % (alphas[0], alphas[1],), iaa.ContrastNormalization(alpha=alphas, per_channel=True)) for alphas in [(0.4, 0.6), (0.65, 0.85), (0.9, 1.1), (1.15, 1.35), (1.4, 1.6)]]),
        ("Grayscale", [("alpha=%.1f" % (alpha,), iaa.Grayscale(alpha=alpha)) for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]]),
        ("PiecewiseAffine", [("scale=%.3f" % (scale,), iaa.PiecewiseAffine(scale=scale)) for scale in [0.015, 0.03, 0.045, 0.06, 0.075]]),
        ("Affine: Scale", [("%.1fx" % (scale,), iaa.Affine(scale=scale)) for scale in [0.1, 0.5, 1.0, 1.5, 1.9]]),
        ("Affine: Translate", [("x=%d y=%d" % (x, y), iaa.Affine(translate_px={"x": x, "y": y})) for x, y in [(-32, -16), (-16, -32), (-16, -8), (16, 8), (16, 32)]]),
        ("Affine: Rotate", [("%d deg" % (rotate,), iaa.Affine(rotate=rotate)) for rotate in [-90, -45, 0, 45, 90]]),
        ("Affine: Shear", [("%d deg" % (shear,), iaa.Affine(shear=shear)) for shear in [-45, -25, 0, 25, 45]]),
        ("Affine: Modes", [(mode, iaa.Affine(translate_px=-32, mode=mode)) for mode in ["constant", "edge", "symmetric", "reflect", "wrap"]]),
        ("Affine: cval", [("%d" % (int(cval*255),), iaa.Affine(translate_px=-32, cval=int(cval*255), mode="constant")) for cval in [0.0, 0.25, 0.5, 0.75, 1.0]]),
        (
            "Affine: all", [
                (
                    "",
                    iaa.Affine(
                        scale={"x": (0.5, 1.5), "y": (0.5, 1.5)},
                        translate_px={"x": (-32, 32), "y": (-32, 32)},
                        rotate=(-45, 45),
                        shear=(-32, 32),
                        mode=ia.ALL,
                        cval=(0.0, 1.0)
                    )
                )
                for _ in sm.xrange(5)
            ]
        ),
        ("ElasticTransformation\n(sigma=0.2)", [("alpha=%.1f" % (alpha,), iaa.ElasticTransformation(alpha=alpha, sigma=0.2)) for alpha in [0.1, 0.5, 1.0, 3.0, 9.0]])
    ]

    print("[draw_per_augmenter_images] Augmenting...")
    i = 0
    for (row_name, augmenters) in rows_augmenters:
        for img_title, augmenter in augmenters:
            aug_det = augmenter.to_deterministic()
            image_aug = aug_det.augment_image(image)
            #print(outputDir + os.path.splitext(os.path.basename(imgName))[0] + "_%04d.jpg"% (i,))
            misc.imsave(outputDir + os.path.splitext(os.path.basename(imgName))[0] + "_%04d.jpg" % (i,), image_aug)
            i += 1

if __name__ == "__main__":
	main()
