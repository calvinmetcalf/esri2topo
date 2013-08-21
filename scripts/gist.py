from arcpy import AddMessage,GetParameterAsText
from esri2open import toOpen
from tempfile import mkdtemp
from os import remove, rmdir,path, sep
from urllib2 import Request, urlopen
from base64 import b64encode
from json import dumps,loads
from topojson import topojson

def getName(feature):
    if feature[0] in ("'",'"'):
        feature = feature[1:-1]
    name = path.splitext(path.split(feature)[1])
    if name[1]:
        if name[1]==".shp":
            return name[0]
        else:
            return name[1][1:]
    else:
        return name[0]

def doStuff(inFile,login,description):
    base = mkdtemp()
    oName = getName(inFile)
    outFile = base+'//'+oName+'.geojson'
    outTopo = base+'//'+oName+'.topojson'
    toOpen(inFile,outFile,"geojson")
    topojson(outFile,outTopo)
    postGist(outFile,oName,login,description)
    cleanUp(base,outFile,outTopo)

def cleanUp(p,f,t):
    remove(f)
    remove(t)
    rmdir(p)
    

def dealLogin(req,login):
    if login == 'NONE':
        return
    req.add_header('Authorization','Basic '+b64encode(login))

def postGist(outFile,filename,login,description):
    newUrl = 'https://api.github.com/gists'
    baseFile = open(outFile,'r')
    data = {"public":True,"files":{filename+".topojson":{'content':baseFile.read()}}}
    baseFile.close()
    if description:
        data['description']=description
    req = Request(newUrl)
    req.add_header('Content-Type', 'application/json')
    dealLogin(req,login)
    resp = urlopen(req,dumps(data))
    r = loads(resp.read())
    url = 'https://gist.github.com'+r['url'][r['url'].rfind('/'):]
    AddMessage(url)

doStuff(GetParameterAsText(0),GetParameterAsText(1),GetParameterAsText(2))