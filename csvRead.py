#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
import csv
# #######################################################################################   Global Vars
sourceAddr = "/home/justin/"

# #######################################################################################   Fxns



# #######################################################################################   MAIN CODE START
# ---------------------------------------------------------------- parse arguments passed
parser = argparse.ArgumentParser(description='')

parser.add_argument('-s', type=str, default='', dest='csvSource', help='orig text file')

parsedArgs = parser.parse_args()

print "\n> Using " +parsedArgs.csvSource+ " as text source"

with open(parsedArgs.csvSource, 'rb') as f:
    reader = csv.reader(f)
    for line in reader:
        print sourceAddr + line[0] + " " + line[1]
        





