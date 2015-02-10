#!/usr/local/bin/python3
"""
-------------------------------------------------------------------------------
CST205_PIL.PY

AUTHOR(S):     Peter Walker    pwalker@csumb.edu

PURPOSE-  This module will be used by CST 205 for image manipulation. It
            creates some classes that will use the PIL package (installed
            by calling 'pip3 install Pillow')

CLASSES-
    ..
-------------------------------------------------------------------------------
"""


# IMPORTS
import os
import sys
import subprocess
from numpy import asarray
from tkinter.filedialog import (askdirectory, askopenfilename)
from PIL import Image
#END IMPORTS



#CLASS
class RGBPixel(object):
    __red = 0
    __green = 0
    __blue = 0
    x=0; y=0

    def __init__(self, r=0,g=0,b=0, x=0,y=0):
        """
        Object initialization
        ARGS:
            self    this Object
            r       A pixel value for the Red aspect
            g       A pixel value for the Green aspect
            b       A pixel value for the Blue aspect
            x       The X-part of the this pixel's location within the picture
            y       The Y-part of the this pixel's location within the picture
        """
        self.__red = r
        self.__green = g
        self.__blue = b
        self.checkVals()
        self.x = x
        self.y = y

    def checkVals(self):
        while (self.__red>255):
            self.__red = self.__red-256
        while (self.__green>255):
            self.__green = self.__green-256
        while (self.__blue>255):
            self.__blue = self.__blue-256
    #END DEF

    def setRed(self, val):
        self.__red = val
        self.checkVals()
    def getRed(self):
        return self.__red

    def setGreen(self, val):
        self.__green = val
        self.checkVals()
    def getGreen(self):
        return self.__green

    def setBlue(self, val):
        self.__blue = val
        self.checkVals()
    def getBlue(self):
        return self.__blue

    def _as_array(self):
        return [self.__red, self.__green, self.__blue]
    def _as_tuple(self):
        return (self.__red, self.__green, self.__blue)

    def cdist(self, **kwargs):
        """
        Gets the color distance between this pixel and a specified color or pixel object
        ARGS:
            color   tuple, 3 integer values where 0<=x<=255
            pixel   an RGBPixel object
        RETURNS:
            A Float, that is this pixel's color's distance to the given RGBPixel or
             color tuple.
            A negative number means that this pixel will likely be lighter, while
             a positive number means that this pixel will likely be darker
        """
        if not any( [elem in kwargs for elem in ["color", "pixel"]] ):
            raise KeyError("You must pass either a color or pixel through the keywords 'color' or 'pixel'")
        if "color" in kwargs:
            if not (isinstance(kwargs['color'], tuple) or isinstance(kwargs['color'], list)) \
                    and len(kwargs['color']) != 3:
                raise ValueError("You must give an RGB value as a tuple (r,g,b) to 'color'")
        elif "pixel" in kwargs:
            if (self.__class__ != kwargs['pixel'].__class__):
                raise ValueError("You must give an RGBPixel object to 'pixel'")
        #END IF/ELIF
        if "color" in kwargs:
            givenR, givenG, givenB = kwargs['color']
        elif "pixel" in kwargs:
            givenR, givenG, givenB = kwargs['pixel']._as_tuple()
        rDist = givenR-self.__red
        gDist = givenG-self.__green
        bDist = givenB-self.__blue
        return ((rDist+gDist+bDist)/3.0)
    #END DEF

    def ldist(self, pixel):
        """
        Returns the length distance between two RGBPixels according to their
         X and Y values.
        """
        if not isinstance(pixel, self.__class__):
            raise ValueError("You must pass an RGBPixel to this function")
        xDist = pixel.x-self.x
        yDist = pixel.y-self.y
        from math import sqrt
        return sqrt(xDist**2 + yDist**2)
    #END DEF

    def __str__(self):
        return ("Pixel at ("+str(self.x)+","+str(self.y)+"): "+
                "RED="+str(self.__red)+", GREEN="+str(self.__green)+", BLUE="+str(self.__blue))
    #END DEF
#END CLASS



#CLASS
class RGBImage(object):
    # ---------------------
    # Class Attributes
    inputFilename = ""
    outputFilename = ""

    __myImage = None
    pixels = []

    height = 0
    width = 0
    # ---------------------

    def __init__(self, filename="", saveTo="", blank=False, width=100, height=100):
        """
        Object initialization
        ARGS:
            self        this Object
            filename    String, the location of the picture
            saveTo      String, the location that this picture will be saved to
            blank       Boolean, whether this image should be a blank image
                width   Integer, the width of the blank image
                height  Integer, the height of the blank image
        """
        self.pixels = []
        if not blank:
            if not filename:
                self.inputFilename = askopenfilename( initialdir = os.path.expanduser("~"),
                                            title = "Select the FILE containing the raw data",
                                            multiple = False)
            else:
                self.inputFilename = os.path.abspath(filename)
                if not os.path.isfile(self.inputFilename) or \
                        self.inputFilename.split(".")[-1].lower() not in ["jpg","jpeg","png","gif"]:
                    raise ValueError("You must pass in a legitimate picture file")
            #END IF/ELSE
            if not saveTo:
                self.outputFilename = (self.inputFilename.rsplit(".",1)[0] + "_v2." +
                                        self.inputFilename.rsplit(".",1)[1])
            else:
                self.outputFilename = os.path.abspath(saveTo)
            #END IF/ELSE
            if os.path.isfile(self.outputFilename):
                print("'{}' will be overwritten if this file is saved. "+
                    "Consider saving to another location.".format(self.outputFilename.split("/").split("\\")[-1]))
            #END IF
            self.__myImage = Image.open(self.inputFilename)
        else:
            self.__myImage = Image.new("RGB", (width, height))
        #END IF/ELSE

        #The results of calling asarray() on the now created Image object is a 4-dimensional
        # array. The original array is made up of rows, each row is made up of pixels, and
        # each pixel is a set of 3 values (R,G,B of the pixel)
        tmpPixels = asarray(self.__myImage)
        #Now we are going to mirror the structure of the return of asarray(), only each
        # pixels will now be an object
        rowCount = 0
        for row in tmpPixels:
            self.pixels.append([])
            colCount = 0
            for pixel in row:
                self.pixels[-1].append( RGBPixel(*pixel, x=colCount, y=rowCount) )
                colCount+=1
            #END FOR
            rowCount+=1
        #END FOR

        #Setting some other useful variables for users
        self.width, self.height = self.__myImage.size

        #Finally closing the image
        self.__myImage.close()
    #END DEF

    def getPixel(self, *args):
        """
        Gets an RGBPixel object at the specified (x,y) coordinate
        ARGS:
            self    this Object
            x       The X coordinate of the pixel
            y       The Y coordinate of the pixel
                or
            (x,y)   The X and Y coordinate within a tuple or list
        RETURNS:
            RGBPixel object
        RAISES:
            ValueError - 'x' or 'y' is out of the picture's bounds
        """
        #Getting the X and Y from the passed arguments
        if (isinstance(args[0], tuple) or isinstance(args[0], list)) and len(args[0])>1:
            x,y = args[0]
            if not(isinstance(x,int) and isinstance(y,int)):
                raise ValueError("The first two elements of the tuple you passed were not integers")
        elif (isinstance(args[0],int) and isinstance(args[1],int)):
            if (args[0]>self.width):
                raise ValueError("This pixel location is not within this picture bounds.")
            if (args[1]>self.height):
                raise ValueError("This pixel location is not within this picture bounds.")
            x = args[0]
            y = args[1]
        else:
            raise ValueError("You must either pass in a 2-tuple of integers, or two integers")
        return self.pixels[y][x]
    #END DEF

    def save(self, filename="", forceOverwrite=False):
        """
        This will save the current object to a specified location
        ARGS:
            self            this Object
            filename        OPTIONAL. String, the location to be save to.
            forceOverwrite  OPTIONAL. Boolean, whether to force overwrite of file
                             at location 'filename' or 'self.outputFilename'
        RETURNS:
            none
        RAISES:
            none.
            Will ask user if they wish to overwrite a file if it exists at the given
             location in filename, or at self.outputFilename
        """
        if filename:
            self.outputFilename = os.path.abspath(filename)
        if os.path.isfile(self.outputFilename) and not forceOverwrite:
            overwrite = input("{} will be overwritten. Continue? (y/n) ".format(self.outputFilename))
            if overwrite.lower() != "y":
                return
        #END IF
        #array needs to be an array of rows, each row needs to be an array of
        # pixels, and each pixel an array of pixel values (R,G,B)
        img_to_array = asarray(self.__as_array())
        Image.fromarray(img_to_array).save(self.outputFilename)
        del img_to_array
    #END DEF

    def show(self):
        """Shows the image the user is currently working on"""
        img_to_array = asarray(self.__as_array())
        Image.fromarray(img_to_array).show()
        del img_to_array
    #END DEF

    def __as_array(self):
        """
        Converts the 3-dimensional array of pixel objects into a 4-dimensional
         array of RGB values (each pixel object is converted to an array)
        """
        tempArray = []
        for row in self.pixels:
            tempArray.append([])
            for pixel in row:
                tempArray[-1].append(pixel._as_array)
        #END FOR
        return tempArray
    #END DEF

    def __str__(self):
        """Returns a string representation of this object"""
        return ("RGB Image named "+self.inputFilename.split("/")[-1].split("\\")[-1]+"\n"+
                "Size is "+str(self.width)+"x"+str(self.height)+" pixels")
    #END DEF
#END CLASS