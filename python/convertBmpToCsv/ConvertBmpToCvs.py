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
# 32 – 63  -> Yellow
# 64 – 127 -> Red // turn on turbulence bit
#
def convertToCsv(iImage):

    finalSize = 128, 128
    image = iImage.resize(finalSize) # resize using nearest filter

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
                #b = b | random.randint(32, 63) # 63
                b = b | 63 # 63
            elif v[0] > 0 : # only red
                #b = b | random.randint(32, 63)
                b = b | 1 << 6 # flip the turbulence bit
            elif v[1] > 0: #only  green
                #b = b | random.randint(16,31) # 31
                b = b | 31 # 31
                
            csv +=  str(b) + ","
        csv += "\n"

    # remove 2 last character
    csv = csv[:-2]
    # add \n
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
#--- MAIN
#------------------------------------------------------------------------------

if(len(sys.argv) >= 3):
    folderPath = sys.argv[1]
    outputCsvFileName = sys.argv[2]
    print("Converting bmp images from: %s" % folderPath)

    # glob all bmp in folder
    slicesToProject = glob.glob(folderPath + "/*.bmp")

    # we need at least on image and we assume all slice size equals
    sliceSize = 0, 0
    if(len(slicesToProject) >= 1):
        slice = Image.open(slicesToProject[0])
        sliceSize = slice.size
        print("Slice size: (%d, %d)" % (sliceSize[0],sliceSize[1]))

    # create an image where we will project all slices
    sliceProjections = Image.new('RGB', sliceSize, (0,0,0))
    for slicePath in slicesToProject:
        print("Projecting slice %s" % slicePath)
        slice = Image.open(slicePath)

#newSize = sliceSize[0] / 4, sliceSize[1] / 4
#slice = slice.resize( newSize )
#slice.save(slicePath, "BMP")

        sourcePixels = slice.load()
        destinationPixels = sliceProjections.load()

        # for each pixel write to the sliceProjections if value is greater.
        for y in range(sliceSize[1]):
            for x in range(sliceSize[0]):
                sourceValue = sourcePixels[x, y]
                destinationValue = destinationPixels[x, y]

                if isGreater(sourceValue, destinationValue):
                    destinationPixels[x, y] = sourceValue

    # save just to visualy inspect
    # save as jpeg so it is not glob by the bmp filter on line 90
    sliceProjections.save(folderPath + "/sliceProjections.jpeg", "JPEG")

    # convert sliceProjections to a csv file
    csvContent = convertToCsv(sliceProjections);
    csvFile = open(folderPath + "/" + outputCsvFileName,"w+")
    csvFile.write(csvContent)
    csvFile.close()

else:
    m = '''Invalid number Of arguments:
    1- Provide a folder path to the images slices
    2- Provide the output name of the csv file

    Ex: python ConvertBmpToCsv ./Archive output.csv
    '''
    print(m)

