#----------------------------------------------------------------------------------
# Copyright 2013 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#----------------------------------------------------------------------------------
# MilitaryUtilities.py
# Description: Miscellaneous shared objects and methods
#----------------------------------------------------------------------------------

import sqlite3
import uuid
import re
import arcpy
import os
import SymbolDictionary
import GeometryConverter
import DictionaryConstants

# IMPORTANT: assumes Mil2525C.dat is at ../../data/dictionary
currentPath = os.path.dirname(__file__)
dataPath = os.path.normpath(os.path.join(currentPath, r"../../data/"))
dictionaryPath = os.path.normpath(os.path.join(dataPath, r"dictionary/"))
geoDatabasePath = os.path.normpath(os.path.join(dataPath, r"geodatabases/"))
symbolDictionaryPath = os.path.join(dictionaryPath,  "Mil2525C.dat" )
symbolDictionary = SymbolDictionary.SymbolDictionary(symbolDictionaryPath)
geoConverter = GeometryConverter.GeometryConverter(symbolDictionary)

def pointsToArcPyGeometry(pointList, shapeType) : 

    arcPoint = arcpy.Point()
    arcArray = arcpy.Array()
       
    for point in pointList : 
        x = point.split(',')[0]
        y = point.split(',')[1]
        print "(", x, ",", y, ")"
        arcPoint.X = float(x)
        arcPoint.Y = float(y)
        arcArray.add(arcPoint)

    if shapeType == "Point" : 
        return arcPoint
    elif shapeType == "Polyline" : 
        arcPolyline = arcpy.Polyline(arcArray)
        return arcPolyline
    elif shapeType == "Polygon" : 
        arcPolygon = arcpy.Polygon(arcArray)
        return arcPolygon
              
def parsePartToControlPoints(part):
    controlPoints = ""
    sep = ""
    
    for subpart in part:
        try:
            # assume it's a point
            subpartStr = str(subpart.X) + "," + str(subpart.Y)
            controlPoints = controlPoints + sep + subpartStr
            sep = ";"
        except AttributeError:
            # it's an array of parts, i.e. a part
            controlPoints = controlPoints + sep + parsePartToControlPoints(subpart)
            sep = ";"
            
    return controlPoints

def parseGeometryToControlPoints(geom):
    try:
        # assume it's a point
        return str(geom.X) + "," + str(geom.Y)
    except AttributeError:
        # it's not a point
        try:
            controlPoints = ""
            sep = ""
            for i in range(geom.partCount):
                part = geom.getPart(i)
                # part is an array
                for subpart in part:
                    controlPoints = controlPoints + sep + parsePartToControlPoints(part)
                    sep = ";"
            return controlPoints
        except AttributeError:
            # it's a part
            return parsePartToControlPoints(geom)
             
def reverseControlPoints(string):
    revnums = re.split(r'(\;+)', string)
    revnums.reverse()
    revnums = ''.join(revnums)
    return revnums
