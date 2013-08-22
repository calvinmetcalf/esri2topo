from arcpy import GetParameterAsText, AddMessage
from esri2open import toOpen
from os import path, sep, remove, rmdir
from tempfile import mkdtemp
from json import load,dump
from topojson import topojson
from random import randint
def getName(feature):
    name = path.splitext(path.split(feature)[1])
    if name[1]:
        if name[1]==".shp":
            return name[0]
        else:
            return name[1][1:]
    else:
        return name[0]
    
features = GetParameterAsText(0).split(";")
outFile = GetParameterAsText(1)
outStuff = {}
tmpdir=mkdtemp()
for feature in features:
    if feature[0] in ("'",'"'):
        feature = feature[1:-1]
    outName = getName(feature)
    outPath = tmpdir+'//'+str(randint(0,1000000))+'temp.geojson'
    if path.exists(outPath):
        remove(outPath)
    toOpen(feature,outPath)
    outStuff[outName]=load(open(outPath))
    remove(outPath)
    #AddMessage(outName)
topo = topojson(outStuff)
dump(topo,open(outFile,'w'))
rmdir(tmpdir)
