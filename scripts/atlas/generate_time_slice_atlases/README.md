# MQM Automated Data Generation

## Generate Time Slice Atlases

generate_time_slice_atlases.py uses an OSM PBF history file to generate atlases for 2 timestamps. 
The PBF is cut to polygon boundaries, given in geojson form. 
Then those area extracts are time sliced using two provided time stamps.
The time slices are cleaned, so that deleted nodes are not included.
Finally, the time slices are converted to atlas files. 

Python Requirements:  
python 3.6+

The following non-python programs are required to be installed and callable from the command line:  
[java 8-11](https://www.java.com/en/download/manual.jsp)  
[osmium-tool](https://osmcode.org/osmium-tool/)

### Usage
`generate_time_slice_atlases.py pbf_path geojsons_folder_path timestamp1 timestamp2 atlas_jar country_boundary_map iso_codes`

|Argument|Description|Example|
|---|---|---|
|pbf_path|Path to an OSM PBF history file.|history/usa_history.osh.pbf|
|geojsons_folder_path|Path to a directory of geojson boundary files. Each file should only contain one (multi)polygon (see '(MULTI)POLYGON FILE FORMATS' [here](https://docs.osmcode.org/osmium/latest/osmium-extract.html)).|geojsons/|
|timestamp1|First timestamp to make atlases for. Format: yyyy-mm-ddThh:mm:ssZ|2018-01-01T00:00:00Z|
|timestamp2|Second timestamp to make atlases for. Format: yyyy-mm-ddThh:mm:ssZ|2019-01-01T00:00:00Z|
|atlas_jar|Path to a shaded jar file of [Atlas](https://github.com/osmlab/atlas).|jars/atlas-5.7.2-SNAPSHOT-shaded.jar|
|country_boundary_map|Path to an Atlas [country boundary](https://github.com/osmlab/atlas/tree/dev/src/main/java/org/openstreetmap/atlas/geography/boundary) map for the geojson boundaries.|boundary_maps/country_boundary_map.shp|
|iso_codes|ISO country codes from the country boundary map to generate atlases for.|CAN,MEX,USA|
