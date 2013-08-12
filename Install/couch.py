from arcpy import AddMessage,GetParameterAsText
from esri2open import toOpen
from tempfile import mkdtemp
from os import remove, rmdir
from urllib2 import Request, urlopen, HTTPHandler, build_opener
from base64 import b64encode
from json import dumps
previewPage = """
<!doctype html>
<html lang="en">
    <head>
    	<meta charset='utf-8'/>
		<title>
			ESRI To Couch
		</title>
		<link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.css" />
		<!--[if lte IE 8]>
			<link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.ie.css" />
		<![endif]-->
		<style>
			html { height: 100% }
			body { height: 100%; margin: 0; padding: 0;}
			#map{ height: 100% }
		</style>
	</head>
	<body>
		<div id="map"></div>
		<script src="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.js"></script>
		<script>
			function fileLoaded(geoJSON){
				var map = L.map('map');
				var geoJSONLayer = L.geoJson(geoJSON,{onEachFeature:function(feature,layer){
					var key,popup;
					if(feature.properties){
						popup="<ul>";
						for(key in feature.properties){
							popup += "<li>"
							popup += key;
							popup += " : ";
							popup += feature.properties[key];
							popup += "</li>"
						}
						popup += "</ul>";
						layer.bindPopup(popup);
					}
				}});
				map.fitBounds(geoJSONLayer.getBounds());
				L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg', {
					attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
					subdomains: '1234'
				}).addTo(map);
				geoJSONLayer.addTo(map);
			}
		</script>
		<script src="all?callback=fileLoaded"></script>
	</body>
</html>
"""
design = dumps({
   "_id": "_design/geojson",
   "spatial": {
       "geo": "function(doc){\n       if(doc.geometry){ emit(doc.geometry,doc)};\n            }"
   },
   "views": {
       "geometry": {
           "map": "function(doc) {\n  if(doc.geometry){\nemit(doc.geometry,doc);\n}\n}"
       }
   },
   "indexes":{
       "geo":{
           "index":"function(doc){\n  if (doc.geometry&&doc.geometry.type===\"Point\"){\n    \n    index('lat', doc.geometry.coordinates[1], {\"store\":\"yes\"});\n    index('lon', doc.geometry.coordinates[0], {\"store\":\"yes\"});\n  \n  for(var key in doc){\n      if ([\"_rev\",\"_id\",\"geometry\"].indexOf(key)===-1&&(typeOf doc[key]===\"string\"||typeOf doc[key]===\"number\")){\n        index(key, doc[key], {\"store\":\"yes\"});\n      }\n    }\n  \n}\n}"
           }
       },
   "rewrites": [
       {
           "to": "/_list/geojson/geometry",
           "from": "/all"
       },
       {
           "to": "/index.html",
           "from": "/"
       }
   ],
   "_attachments": {
        "index.html" : {
            "content_type" : "text/html",
            "data" : b64encode(previewPage)
        }
    },
   "lists": {
       "geojson": "function(head, req) {\n    var row, out, sep = '\\n';\n    if (req.headers.Accept.indexOf('application/json')!=-1) {\n        start({\"headers\":{\"Content-Type\" : \"application/json\"}});\n    }    else {\n        start({\"headers\":{\"Content-Type\" : \"text/plain\"}});\n    }\n    if ('callback' in req.query) {\n        send(req.query['callback'] + \"(\");\n    }    send('{\"type\": \"FeatureCollection\", \"features\":[');\n    while (row = getRow()) {\n        out = {type: \"Feature\", geometry: row.value.geometry};\n\t\t\t\tdelete row.value.geometry;\n               out.properties= row.value\n        send(sep + JSON.stringify(out));        sep = ',\\n';\n    }\n    send(\"]}\");\n    if ('callback' in req.query) {\n        send(\")\");}};\n"
   },
   "validate_doc_update": "function(newDoc, oldDoc, userCtx) {  if (userCtx.roles.indexOf('_admin') !== -1) {    return;  } else {    throw({forbidden: 'Only admins may edit the database'});  }}"
})

def doStuff(inFile,dbUrl,login,createDB):
    base = mkdtemp()
    outFile = base+'//output.json'
    toOpen(inFile,outFile,"geojson")
    postToCouch(dbUrl,outFile,login,createDB)
    cleanUp(base,outFile)

def cleanUp(p,f):
    remove(f)
    rmdir(p)

def dealLogin(req,login):
    if login == 'NONE':
        return
    req.add_header('Authorization','Basic '+b64encode(login))

def postToCouch(url,outFile,login,createDB):
    if createDB=='true' and login != 'NONE':
        opener = build_opener(HTTPHandler)
        res3 = Request(url)
        dealLogin(res3,login)
        res3.get_method = lambda: 'PUT'
        opener.open(res3)
        arcpy.AddMessage("Created DB")
    newUrl = url + '//_bulk_docs'
    baseFile = open(outFile,'r')
    data = baseFile.read()
    baseFile.close()
    req = Request(newUrl)
    dealLogin(req,login)
    req.add_header('Content-Type', 'application/json')
    urlopen(req,data)
    arcpy.AddMessage("Added Rows")
    if login != 'NONE':
        req2 = Request(url)
        dealLogin(req2,login)
        req2.add_header('Content-Type', 'application/json')
        urlopen(req2,design)
        arcpy.AddMessage("Added Design Doc")
        arcpy.AddMessage("View it at "+url+"/_design/geojson/_rewrite/")

doStuff(arcpy.GetParameterAsText(0),arcpy.GetParameterAsText(1),arcpy.GetParameterAsText(2),arcpy.GetParameterAsText(3))
