from arcpy import GetParameterAsText
from esri2open import toOpen
from topojson import topojson
from tempfile import mkdtemp
from os import remove, rmdir,path
dr = mkdtemp()
tempfl = dr + path.splitext(path.split(GetParameterAsText(1))[1])[0]+'.geojson'
toOpen(GetParameterAsText(0),tempfl,"geojson")
topojson(tempfl,GetParameterAsText(1))
remove(tempfl)
rmdir(dr)