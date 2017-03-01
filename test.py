#!/usr/bin/env python

import subprocess
import sys
import os
import argparse

path = "/home/sub/file.txt"

newPath = os.path.dirname(path)

lastSlashIndex = newPath.rfind('/')

result = newPath[lastSlashIndex+1:]
print result













