# -*- coding: utf-8 -*-

import random
import glob
import math
import sys
from PIL import Image

#------------------------------------------------------------------------------
# Converts the input image to a csv file.
# each element of the csv file is 1 Byte and is encoded as follow.
#
# the function returns the csv string.
#
# PWS: Predictive windshear
# T: Turbulence
# P: Precipitation
#  
# | 7 | 6 | 5 4 3 2 1 0 |
# |PWS| T |      P      |
#  
# PWS bit can be on or off
# Turbulence bit can be on or off
# Precipitation value can be [0, 63]
#  
# Colors are derived from the whole 8 bits pattern
# and goes as follow:
#  
# 0 – 15   -> Black
# 16 – 31  -> Green
# 32 – 47  -> Yellow
# 48 – 63 -> Red
#
def convertToCsv(iImage):

    finalSize = 128, 128
    image = iImage.resize(finalSize) # resize using nearest filter

    # rotate 90 degrees counter clockwise
    # we do this so the radar imags matches the storm in aXion
    # the problem might be in axion, but much simpler to rotate the image at this point...
    #
    image = image.rotate(90) 

    csv = ""
    pixels = image.load()
    size = image.size
    for y in range(size[1]):
        for x in range(size[0]):
            v = pixels[x, y]

            b = 0;
            
            if v == (0, 0, 0): # if black
                b = 0
            elif v[1] > 0 and v[0] > 0: # is yellow
                b = b | 40
            elif v[0] > 0 : # only red
                b = b | 55
                b = b | 1 << 6 # flip the turbulence bit
            elif v[1] > 0: #only  green
                b = b | 20
                
            csv +=  str(b) + ","
        csv += "\n"

    return csv

#------------------------------------------------------------------------------
def isGreater(iSourceRgb, iDestinationRgb):
    r = False

    # priority is as follow, from high to low
    # red, yellow, green
    if iSourceRgb[0] > 0 or iSourceRgb[1] > iDestinationRgb[1] or iSourceRgb[2] > iDestinationRgb[2]:
        r = True;

    return r;

#------------------------------------------------------------------------------
def makeGradientCsv():
    csv = ""

    for y in range(128):
        for x in range(128):
            csv += str(y/2) + ","
        csv += "\n" 

    csvFile = open("./gradientFile.csv","w+")
    csvFile.write(csv)
    csvFile.close()
    return;

#------------------------------------------------------------------------------
#--- MAIN
#------------------------------------------------------------------------------

if(len(sys.argv) >= 3):
    inputImagePath = sys.argv[1]
    outputCsvFileNamePath = sys.argv[2]
    print("Converting bmp image: %s" % inputImagePath)

    sliceSize = 0, 0
    slice = Image.open(inputImagePath)
    sliceSize = slice.size
    print("Slice size: (%d, %d)" % (sliceSize[0],sliceSize[1]))

    # convert sliceProjections to a csv file
    csvContent = convertToCsv(slice);
    csvFile = open(outputCsvFileNamePath,"w+")
    csvFile.write(csvContent)
    csvFile.close()

elif(len(sys.argv) == 2 and sys.argv[1] == "makeGradient"):
    makeGradientCsv()
else:
    m = '''Invalid number Of arguments:
    1- Provide a folder path to the images slices
    2- Provide the output name of the csv file

    Ex: python ConvertBmpToCsv ./Archive/storm_1_1.bmp ./output.csv
    '''
    print(m)

