#esri2topo

##topojson from your arcmap!

Usage
------
1. Copy the .tbx file and the .py file to any local directory
2. With ArcGIS desktop software running (e.g. ArcCatalog), add the .tbx file to your tool box by right clicking and choosing 'Add Toolbox'.
3. Double click on the which script you want to run which are

ESRI To Topo
---------
Output one feature to TopoJSON, arguments are:

* `Feature Class`: the name of the Feature Class you want to export
* `Output File`: the output topojson

ESRI To Topo (merge)
---------
Output multiple feature classes to one TopoJSON file, arcs shared by both features will be only stored once:

* `Feature Classes`: the name of the Feature Class you want to export
* `Output File`: the output topojson

ESRI To Gist
---------
Export and upload a feature class to gist.github.com as TopoJSON:

* `Layer`: The names of the layer you want to export
* `Login`: Github login information in the `user:pw` format, optional will otherwise be an anonymous gist.
* `Description`: Check if you want the DB to be created, requires login.

License
-------
MIT

